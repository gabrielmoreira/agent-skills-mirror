#!/usr/bin/env python3
"""Offline full interview adapter. No network, native actions, or implicit saving."""
import argparse
import json
import sys
import guardian
import interview_flow as flow


class _PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default diagnostics reproduce unknown options and values.
        # The structured failure must not contain any of those private inputs.
        raise flow.InterviewError('Invalid interview command arguments') from None

    def _print_message(self, message, file=None):
        # argparse otherwise ignores write failures and can claim --help worked.
        if message:
            stream = file if file is not None else sys.stderr
            stream.write(message)
            stream.flush()


def _emit_result(result, *, indent=None):
    try:
        print(json.dumps(result, ensure_ascii=False, indent=indent), flush=True)
        return True
    except (OSError, ValueError):
        # Never report successful delivery or expose a raw stream error. stderr
        # may also be unavailable; the nonzero exit remains authoritative then.
        try:
            print(json.dumps({'status': 'blocked', 'code': 'INTERVIEW_OUTPUT_FAILED',
                              'action_executed': False, 'saved': result.get('saved', False)}),
                  file=sys.stderr, flush=True)
        except (OSError, ValueError):
            pass
        return False


def main(argv=None):
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='strict')
        parser=_PrivateArgumentParser(prog='interview_cli.py', description=__doc__)
        parser.add_argument('--input', help='Previously explicitly saved private state JSON')
        parser.add_argument('--target-ref', help='Target alias; must match when resuming')
        parser.add_argument('--account-ref', help='Account alias; must match when resuming')
        parser.add_argument('--answer-file', help='Local JSON: one question_id/value/state/source answer, or {"answers": [same answer objects]} from one reply')
        parser.add_argument('--context-file', help='Explicit host routing facts; not action permission')
        parser.add_argument('--resume', help='Actual interruption event label; requires --input, not an authorization token')
        parser.add_argument('--resume-review-file', help='Current normalized reply: resume_id/response/source, optional changed_keys/reported_at')
        parser.add_argument('--subscription-conflict-file', help='Actual current contradiction: source, optional observed_at/current_reply; no service access')
        parser.add_argument('--subscription-resolution-file', help='Current normalized evidence bound to the exact subscription episode/account/device/task')
        parser.add_argument('--output', help='Opt-in private state file; never overwrites')
        parser.add_argument('--topics', nargs='+', choices=flow.REFERENCE_TOPICS, default=[],
                            help='Normalized topics from the current reply; no questionnaire required')
        parser.add_argument('--reference-os', choices=('unknown', 'macos', 'windows', 'linux', 'mobile_only'), default='unknown')
        parser.add_argument('--references-only', action='store_true', help='Only route references; do not create or save interview state')
        parser.add_argument('--capabilities-file', help='Private target capability observations JSON')
        parser.add_argument('--work-item-file', help='One private handoff or acceptance work item JSON')
        args=parser.parse_args(argv)
        if args.references_only:
            if any(value for key, value in vars(args).items()
                   if key not in {'topics', 'reference_os', 'references_only'}):
                raise flow.InterviewError('Reference-only mode cannot change or save state')
            output = {'required_references': flow.references_for_topics(args.topics, os_name=args.reference_os),
                      'action_executed': False, 'saved': False}
            return 0 if _emit_result(output, indent=2) else 2
        if (args.resume is not None or args.resume_review_file is not None) and not args.input:
            raise flow.InterviewError('Resume requires a saved input state')
        if args.input:
            state=flow.loads_state(json.dumps(guardian.load_json(args.input)))
            if ((args.target_ref is not None and args.target_ref != state['target_alias']) or
                    (args.account_ref is not None and args.account_ref != state['account_alias'])):
                raise flow.InterviewError('Explicit resume target or account mismatch')
        else:
            state=flow.new_state(args.target_ref if args.target_ref is not None else 'target-unconfirmed',
                                 args.account_ref if args.account_ref is not None else 'account-unconfirmed')
        if args.resume is not None:
            state=flow.resume_interview(state,resume_id=args.resume)
        if args.context_file:
            state=flow.set_context(state,**guardian.load_json(args.context_file))
        if args.resume_review_file:
            reply=guardian.load_json(args.resume_review_file)
            required={'resume_id','response','source'}
            if (not isinstance(reply,dict) or not required.issubset(reply)
                    or set(reply)-required-{'changed_keys','reported_at'}):
                raise flow.InterviewError('Invalid resume review envelope')
            state=flow.record_resume_review(state,**reply)
        if args.answer_file:
            item=guardian.load_json(args.answer_file)
            if isinstance(item,dict) and set(item)=={'answers'}:
                answers=item['answers']
            else:
                answers=[item]
            prior=state
            pending=flow.next_question(prior)
            state=flow.record_facts(prior,answers,source='user:current-turn')
            if (pending is not None and pending['clarification']
                    and (pending['id']=='Q-P02' or pending['id']=='Q-C08'
                         and prior['facts'].get('Q-C08',{}).get('state') in {'reported','observed'}
                         and prior['facts'].get('Q-C08',{}).get('value')=='selected_unspecified')
                    and any(answer['question_id']==pending['id'] for answer in answers)):
                # Validate the whole batch first. Then replay that pure update
                # with the delivered identity question consumed; named/refused
                # replies also retain the spent clarification. No partial save.
                state=flow.record_facts(flow.mark_asked(prior,pending['id']),answers,
                                        source='user:current-turn')
        if args.subscription_conflict_file:
            reply=guardian.load_json(args.subscription_conflict_file)
            if not isinstance(reply,dict) or not {'source'}.issubset(reply) or set(reply)-{'source','observed_at','current_reply'}:
                raise flow.InterviewError('Invalid subscription contradiction envelope')
            state=flow.report_subscription_conflict(state,**reply)
        if args.subscription_resolution_file:
            reply=guardian.load_json(args.subscription_resolution_file)
            required={'episode_id','account_ref','target_ref','task_id','outcome','answers','source'}
            if not isinstance(reply,dict) or not required.issubset(reply) or set(reply)-required-{'observed_at','current_reply'}:
                raise flow.InterviewError('Invalid subscription resolution envelope')
            state=flow.resolve_subscription_conflict(state,**reply)
        if args.topics:
            state['reference_topics'] = list(dict.fromkeys(state.get('reference_topics', []) + args.topics))
        if args.capabilities_file:
            state = flow.record_capabilities(state, guardian.load_json(args.capabilities_file))
        if args.work_item_file:
            state = flow.record_work_item(state, guardian.load_json(args.work_item_file))
        question=flow.next_question(state)
        # The pending plan-identity clarification is consumed only by its matching
        # valid reply. Rendering alone must not lose an undelivered question.
        output={'schema_version':'guardian-intake-result/1','question':question,
                'assessment':flow.assessment(state),'contact_control':'host_authorization_required',
                'action_executed':False,'saved':False}
        if output['assessment'].get('follow_up', {}).get('items'):
            output['next_step'] = 'review_follow_up'
        if 'resume_review' in state:
            output['resume_review']=flow.resume_review_prompt(state)
        # Provenance may contain private user text or identifiers. Preserve it in
        # explicitly saved private state, but do not reproduce it on stdout.
        subscription=output['assessment']['current_subscription']
        if subscription['source'] is not None:
            subscription['source']='private-source-retained'
        if args.output:
            serialized=flow.dumps_state(state,host_opt_in=True,scope='private_save')
            guardian.save_new(args.output,serialized+'\n')
            output['saved']=True
        return 0 if _emit_result(output, indent=2) else 2
    except (flow.InterviewError,guardian.GuardianError,KeyError,TypeError,ValueError,OSError):
        _emit_result({'status':'blocked','code':'INVALID_OR_UNAUTHORIZED_INTERVIEW_IO','action_executed':False})
        return 2
    except KeyboardInterrupt:
        _emit_result({'status':'cancelled','action_executed':False})
        return 3

if __name__=='__main__':
    code = main()
    try:
        sys.stdout.flush()
    except (OSError, ValueError):
        # Only the standalone process owns stdout. Close a failed buffered pipe
        # here so Python's shutdown flush cannot emit an unsanitized diagnostic.
        code = 2
        try:
            sys.stdout.close()
        except (OSError, ValueError):
            pass
    raise SystemExit(code)

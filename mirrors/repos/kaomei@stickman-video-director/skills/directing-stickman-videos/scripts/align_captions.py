#!/usr/bin/env python3
"""Optional local Whisper timing adapter. No model download without opt-in."""
import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model', default='base')
    parser.add_argument('--language')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--allow-model-download', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists; will not overwrite')
    if not args.audio.is_file():
        parser.error('Audio file not found')
    try:
        import whisper
    except ImportError:
        parser.error('Optional dependency missing: install openai-whisper, or provide existing aligned captions')
    if args.model not in whisper.available_models():
        parser.error('Use a named official Whisper model')
    cache = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache')) / 'whisper'
    cached = cache / f'{args.model}.pt'
    if not cached.is_file() and not args.allow_model_download:
        parser.error('Model not cached; --allow-model-download is required for a download')
    model = whisper.load_model(args.model if args.allow_model_download else str(cached), device=args.device, download_root=str(cache))
    result = model.transcribe(str(args.audio), language=args.language, word_timestamps=True, fp16=False, verbose=False)
    words = [{k: w[k] for k in ('start', 'end', 'word')} for s in result['segments'] for w in s.get('words', []) if w['end'] > w['start']]
    if not words:
        parser.error('No aligned words returned; inspect the audio')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as output:
        json.dump({'words': words, 'method': 'openai-whisper word_timestamps; human text/timing review required'}, output, ensure_ascii=False, indent=2)
    print(json.dumps({'output': str(args.output.resolve()), 'words': len(words)}))


if __name__ == '__main__':
    main()

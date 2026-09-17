# Chinese calibration for the style pass

Load this file at the style-pass step whenever the target text is Chinese, in any variant, on any route. It changes nothing else about the route. The English ban lists in `style-pass.md` §3 do not transfer word for word; what transfers is the *shape* of the checks — the syntax templates of §2, the restore list of §4, the rhythm check of §5, the whitelist of §7 — and this file says what each shape looks like in Chinese.

Evidence: one measured corpus, HC3-Chinese — 6,586 human and 6,586 ChatGPT answers to the same open-domain questions, GPT-3.5-era ChatGPT, Simplified Chinese, 2023 — analysed with 159 Chinese CTAP features by 朱君輝 et al., CCL 2023 (Z), with Guo et al. 2023 (H) supplying a second measure on the same corpus; a 2025 joke-generation study by 蔣彥廷 and 應以周, CCL 2025 (J), is used only where it contradicts Z. A second source (T), a private human-side measurement of Traditional Chinese long-form journalism (ledger `ZH-NEWS-CORPUS-2026`; about two thousand articles from one unnamed Taiwanese publication, spanning about ten years), supplies presence rates in human prose only; it has no machine side and licenses no human-vs-machine claim. Everything else below is a Sepia inference, or an editorial heuristic marked as such in §4. Stable source identities are in the repository research ledger.

## 1 Measured (Z, per-answer means; H where named)

| Feature | Human | ChatGPT | Unit and note |
|---|---|---|---|
| Sentence-length SD | 9.248 | 6.729 | words (詞); in characters (字) 15.150 vs 12.842 — the gap holds in both units |
| Mean sentence length | 25.067 | 21.823 | words — humans *longer*; in characters 40.893 vs 42.396, the direction flips, so length itself is not a signal |
| Paragraphs per answer | 1.442 | 3.681 | ChatGPT wrote *more* paragraphs; mean paragraph length 123.907 vs 92.747 characters |
| Punctuation density | 0.135 | 0.136 | Z; the same corpus measured as punctuation share of tokens reads 16.0% vs 13.4% (H) — contradictory measures, not a signal |
| 語氣詞 density | 0.016 | 0.003 | five times higher in human answers |
| 連詞 density | 0.013 | 0.036 | 「和」 alone: 4.13 vs 11.76 per answer |
| Pronoun density | 0.052 | 0.069 | second person 0.010 vs 0.021 |
| Monosyllabic word share | 0.483 | 0.379 | disyllabic share 0.445 vs 0.532; disyllabic word count was selected as a key feature by both of Z's filters |
| Type-token ratio | 0.725 | 0.543 | content-word richness 0.822 vs 0.647 |
| Mean dependency distance | 3.900 | 3.659 | longest 29.452 vs 23.991 |

## 1b Presence in human Traditional Chinese journalism (T; human side only)

Rates in human prose. A near-zero rate means the form departs from this register's norm when it appears; it is not a measured machine excess. Nothing here is a per-passage cutoff. The middle column names the kind of quantity each time: per 100k characters, share of articles containing the form, or per-article median.

| Form | Presence (T) and kind of quantity | How to read |
|---|---|---|
| Manner adverb 「X地」 before a verb | 1.9 per 100k chars | Departs from this register when it appears; §2 row (T), journalism only |
| 「很」 : 「非常」 | occurrence ratio ≈ 11:1 | 「非常／十分／極為」 stacking is the departure; one instance is not |
| Paired dash 「──…──」 | 15% of articles contain one; 4 per 100k chars (per-article median 0) | Rarer than the single dash by an order of magnitude, but present; not a departure on its own, and no hunt row |
| Single 「──」 | 61% of articles contain it; 40 per 100k chars | Not a signal |
| Single-glyph 「—」 | 7% of articles contain it | Glyph choice; a register mismatch at most |
| 「……」 | 2% of articles contain it; 0.9 per 100k chars | Departs in narration; inside a quotation it is speech |
| 「綜上所述」「總而言之」 | 0 per 100k chars; 「值得一提的是」 0.1; 「值得注意的是」 0.6 | §3 formula phrases; this register does not use them |
| 「不是…而是」 | 30% of articles contain it; 6.3 per 100k chars | One instance is register-normal; see §4 |
| Three-item 頓號 list (A、B、C) | 59% of articles contain one | Register-normal; see §4 |
| Sentence-initial 「其實」 | 15% of articles contain it | Register-normal; see §4 |
| 「此外」 / 「然而」 | 37% / 53% of articles contain it | Single connectives are register-normal; chaining across clauses is still §2 |
| Sentence bearing any 「」 with no attribution verb (terminology and scare quotes included) | per-article median share 61% | Most 「」 in this register mark terms, not speech; this row says nothing about attribution of speech |
| Sentence bearing a 「」 quotation of 15 characters or more with no attribution verb | per-article median share 33% (q1 20%, q3 50%) | Length is a proxy, not a speech classification: titles, slogans and written statements stay in the pool. Speech quotations as such are unmeasured; this row licenses no restore rule |
| `：「` colon lead-in | 6% of all 「」 quotations; 10% (q1 0%, q3 22%) of quotations of 15 characters or more, per-article medians | Measured on the ordinary quote mark. The colon lead-in exists in this register but is a minority pattern; 「某某表示：「…」」 as the only pattern departs from it |
| Sentence length | per-article median of the mean 59 chars; of the within-article SD 34 | Dispersion is the human trait; length itself is not (consistent with §1 and §5) |
| Runs of three near-equal sentences | per-article median 2 per 100 sentences | §5 as written |
| Suffix-bearing vocabulary 「○○性／○○化／○○感」 | 77 per 100k chars, mostly fixed legal-policy terms | A lexical count only; whether such nouns serve as subjects or wrap a verb (「自我的探索」) was not counted. Nominalized subjects stay unmeasured; §4 row |
| Summary endings | 7 of 169 close-read articles (close-reading sample count) | Conclusion residue (`professional-pass.md` check 7) is the departure in this register |

## 2 What to hunt (Sepia inferences from §1 and §1b; shapes of `style-pass.md` §2)

| Shape | Chinese form | Fix |
|---|---|---|
| Connective stacking (連詞 density 0.036 vs 0.013) | 「和／以及／並且／同時／此外／因此／然而」 chained across clauses; 「和」 joining whole clauses rather than nouns | Delete the connective and let juxtaposition carry the link; Chinese parataxis is the human default |
| Second-person address outside dialogue or instructions | 「你會發現」「您可以」 in expository prose | Delete or recast as a statement |
| Disyllabic padding where a monosyllable is idiomatic | 「進行討論」「加以說明」「予以處理」「做出決定」 | 「討論」「說明」「處理」「決定」 — the verb alone |
| Flat sentence length (SD 6.729 vs 9.248 words) | Runs of adjacent sentences of about the same length | Apply the §5 check as written (runs of three or more adjacent near-equal sentences): split one long sentence, merge two short ones, delete a clause. §5 sets no length cutoff in any language; no Chinese short- or long-sentence share is measured, and none is invented here. Count in whichever unit you use consistently — the SD gap holds in both 詞 and 字. T reports a per-article median mean of 59 characters with within-article SD 34 for journalism, again as dispersion, not a length target |
| Manner adverb 「X地」 before a speech or action verb — journalism only (T: 1.9 per 100k chars in human journalism) | 「緩緩地說」「堅定地表示」「無奈地說」 | In journalistic Chinese, delete the adverb and let the verb, or a following gesture, carry it. Elsewhere (fiction, dialogue tags, technical and incident writing) leave it: the rate is from one journalism register and T says nothing about other registers. Human-side presence, not a measured machine excess |

## 3 What to restore (Sepia inferences; shape of `style-pass.md` §4)

Sprinkled, never poured, and only where the register allows: sentence-final and mid-sentence 語氣詞 (啊、吧、呢、嘛、喔、啦、耶) — the largest measured gap in §1; monosyllabic verbs and adjectives; a spread of sentence lengths; subject ellipsis and colloquial contraction where a native writer would drop the subject, the Chinese counterpart of §4's contractions. Formal venues keep their register: a legal notice does not get 「嘛」. Attribution of speech quotations in journalism is not measured by T (its quotation rows use a length proxy); nothing about attribution is restored on T's account.

## 4 Editorial heuristics — presence measured on the human side only (T), no machine side

Reported by Taiwan editors and readers in 2026 (自由時報 2026-07-12; 數位時代 2026-04-22; ledger "Consulted" table). T gives a presence rate in human journalism for the exact form it counted, named in the last column; forms it did not count stay unmeasured. None has a machine-side number. A single instance of a counted form is register-normal; a cluster in narration is what the §2 template is for. Each is a Chinese form of a template already in `style-pass.md` §2:

| Reported tell | Maps to | Presence in human journalism (T) |
|---|---|---|
| 「不是…而是…」「這不是 X，而是 Y」 | §2 "it's not X, it's Y" | 30% of articles contain 「不是…而是」 (this form only) |
| Nominalized subjects 「○○性／○○感／○○化」 (「自我的探索」 for 「找自己」) | §2 nominalization | Only suffix-bearing vocabulary was counted (77 per 100k chars, mostly fixed legal-policy terms). The subject position and the 「的＋noun」 wrapper were not counted and stay unmeasured; see §1b |
| Three parallel clauses or images, everywhere | §2 rule of three | Only the three-item 頓號 list (A、B、C) was counted: 59% of articles contain one. Parallel clauses and images were not counted and stay unmeasured |
| Paragraph openers 「其實…」「事實上…」; abstractions in quotation marks (「趨勢」「關鍵」「必然」) | §3 formula phrases | Only sentence-initial 「其實」 was counted: 15% of articles contain one. 「事實上」 and quoted abstractions were not counted and stay unmeasured |

## 5 Not signals in Chinese

Punctuation density and comma or period counts (§1: contradictory measures); long sentences counted in words (humans are longer); paragraph count (ChatGPT split *more*, the reverse of the folk belief that AI writes one block); word-frequency level (Z finds humans using commoner words, J finds LLMs doing so — two corpora, two eras, no rule). Mainland Chinese lexicon in a Taiwan venue (視頻、軟件、質量 for 影片、軟體、品質) is a register mismatch under the venue-corpus guardrail in `SKILL.md`, not an AI tell: fix it only when the venue is Taiwanese and the author's own samples do not use it. In Traditional Chinese journalism (T): a single 「不是…而是」, a three-item 頓號 list, a single 「──」, and 「此外」 or 「然而」 standing alone are register-normal (§1b); connectives chained across clauses remain the §2 case.

## 6 Evidence boundary

One corpus, one model era, Simplified Chinese question answering, default un-prompted ChatGPT of 2023. No study measures 2024–2026 models on Chinese narrative or expository prose; J covers single-sentence jokes from four 2025 models and reports lexical richness (human 0.547 vs 0.384–0.461) but no sentence or punctuation statistics. No Taiwan academic study compares human and machine Traditional Chinese; the Taiwan sources above are editorial. Treat every number here as a direction observed once, not a calibration constant. T is one unnamed Taiwanese publication's long-form journalism, about two thousand articles spanning about ten years, human text only, measured privately in 2026-09 and not distributed. It adds presence rates and medians for one register; it has no machine side, so it can only say what is register-normal or worth restoring, never what is a machine tell. Its part-of-speech counts come from jieba on Traditional Chinese and are read as relative values.

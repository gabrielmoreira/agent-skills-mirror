# AGENTS.md

## Project Overview

ဒါဟာ ဝဘ်ဒီဗလပ်မှန်အခြေခံမှုများကို စတင်လေ့လာသူများအတွက် သင်ကြားပေးရန် အရည်အချင်းမြှင့်ပညာရေး သင်ရိုးညွှန်းလမ်းကြောင်း ရှည်လျားသော ထောက်ပံ့မှုပလက်ဖောင်းတစ်ခု ဖြစ်သည်။ သင်ရိုးညွှန်းလမ်းကြောင်းမှာ Microsoft Cloud Advocates မှ ဖန်တီးထားသော 12 နာရီကြာ သင်တန်း ၁၂ ပတ် တစ်ခု ဖြစ်ပြီး JavaScript, CSS, နှင့် HTML ကို မျက်နှာသာသော သင်ခန်းစာ ၂၄ ခု ပါဝင်သည်။

### Key Components

- **ပညာရေး အကြောင်းအရာများ**: စီစဉ်ထားသော သင်ခန်းစာ ၂၄ ခန်းများ၊ စီမံကိန်းလိုက် မော်ဂျူလ်များအဖြစ်
- **လက်တွေ့ ပရောဂျက်များ**: Terrarium, Typing Game, Browser Extension, Space Game, Banking App, Code Editor, နှင့် AI Chat Assistant
- **အပြန်အလှန် စာမေးပွဲများ**: တစ်ခုခြင်း သင်ခန်းစာ မတိုင်မီ နှင့် သင်ခန်းစာပြီးနောက် အကဲဖြတ်ရန် မေးခွန်း ၃ မျိုး ပါဝင်သည့် စာမေးပွဲ ၄၈ ခု
- **ဘာသာစကားပေါင်းများစွာ အထောက်အပံ့**: GitHub Actions မှ တစ်ဆင့် ဘာသာစကား ၅၀ ကျော် အလိုအလျောက် ဘာသာပြန်ခြင်း
- **နည်းပညာများ**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (AI ပရောဂျက်များအတွက်)

### Architecture

- သင်ခန်းစာအခြေခံ ပညာရေး ဒေတာဗေ့စ်
- သင်ခန်းစာ တစ်ခုချင်း အတွင်း README, ကုဒ်နမူနာများ နှင့် နည်းလမ်း ဖြေရှင်းချက်များ ပါဝင်သည်
- စကြာ ဝင်ပေါက်ရှိသော ပရောဂျက်များ ကို ထူးခြားသော ဖိုလ်ဒါများတွင် ထားရှိသည် (quiz-app, စသည်)
- GitHub Actions (co-op-translator) ကို အသုံးပြု၍ ဘာသာပြန်စနစ်
- Docsify ဖြင့် စာရွက်စာတမ်းများကို ဝန်ဆောင်မှုပေးပြီး PDF အဖြစ်လည်းရနိုင်သည်

## Setup Commands

ဒီ ဒေတာဗေ့စ်ကို စင်စစ်ပညာရေး အကြောင်းအရာ အသုံးပြုရုံအတွက် အဓိက ရည်ရွယ်သည်။ အထူးပရောဂျက်များနှင့် လုပ်ကိုင်ရန်အတွက်:

### Main Repository Setup

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App Setup (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # ဖွံ့ဖြိုးမှုဆာဗာကို စတင်ပါ
npm run build      # ထုတ်လုပ်မှုအတွက် တည်ဆောက်ပါ
npm run lint       # ESLint ကို chạyပါ
```

### Bank Project API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # API ဆာဗာ စတင်ပါ
npm run lint       # ESLint ကို ပြေးပါ
npm run format     # Prettier ဖြင့် ပုံစံစစ်ဆေးပါ
```

### Browser Extension Projects

```bash
cd 5-browser-extension/solution
npm install
# ဘရောက်ဇာအသီးသီးထည့်သွင်းနည်းလမ်းညွှန်များကိုလိုက်နာပါ
```

### Space Game Projects

```bash
cd 6-space-game/solution
npm install
# index.html ကို browser မှာဖွင့်ပါ သို့မဟုတ် Live Server ကိုအသုံးပြုပါ
```

### Chat Project (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# GITHUB_TOKEN ပတ်ဝန်းကျင်အပြောင်းအလဲ ကို သတ်မှတ်ပါ
python api.py
```

## Development Workflow

### For Content Contributors

1. **ရိုက်နှိပ်ပြီး fork လုပ်ရန်** မိမိ၏ GitHub အကောင့်သို့
2. **fork ကို clone လုပ်ပါ** ဒေသခံစနစ်သို့
3. **သင်ပြင်ဆင်လိုသော ဗားရှင်း အသစ် ဖန်တီးပါ**
4. သင်ခန်းစာ အကြောင်းအရာ သို့မဟုတ် ကုဒ်နမူနာများ ပြင်ဆင်ပါ
5. ပရောဂျက်တွင် ကုဒ်ပြင်ဆင်မှုများ ရရှိပါက စမ်းသပ်ပါ
6. အကူအညီအဖွဲ့ ဆောင်ရွက်နေသော လမ်းညွှန်ချက်များအတိုင်း pull request တင်သွင်းပါ

### For Learners

1. Fork လုပ် သို့မဟုတ် clone လုပ်ပါ
2. သင်ခန်းစာ ဖိုလ်ဒါများကို နောက်တတ်တိုက် တိုင်ရွက်ပါ
3. သင်ခန်းစာမျက်နှာများကို ဖတ်ရှုပါ
4. https://ff-quizzes.netlify.app/web/ တွင် သင်ခန်းစာမတိုင်မီ စာမေးပွဲ ဖြေဆိုပါ
5. သင်ခန်းစာဖိုလ်ဒါများတွင် ကုဒ်နမူနာများကို လေ့လာပါ
6. အလုပ်အပ်နှင့် စိန်ခေါ်မှုများ ပြီးမြောက်အောင် ဆောင်ရွက်ပါ
7. သင်ခန်းစာပြီးနောက် စာမေးပွဲများ ဖြေဆိုပါ

### Live Development

- **စာရွက်စာတမ်းများ**: ကိုယ်ပိုင် `docsify serve` ကို root တွင်ချပြရန် (port 3000)
- **Quiz App**: quiz-app ဖိုလ်ဒါတွင် `npm run dev` ဖြစ်စေပါ
- **ပရောဂျက်များ**: VS Code ရဲ့ Live Server extension ကို HTML ပရောဂျက်များအတွက် အသုံးပြုပါ
- **API ပရောဂျက်များ**: အဆိုပါ API ဖိုလ်ဒါများတွင် `npm start` ချပြပါ

## Testing Instructions

### Quiz App Testing

```bash
cd quiz-app
npm run lint       # ကုဒ်ပုံစံ ပြဿနာများကို စစ်ဆေးပါ
npm run build      # ဖွဲ့စည်းမှု အောင်မြင်မှုကို အတည်ပြုပါ
```

### Bank API Testing

```bash
cd 7-bank-project/api
npm run lint       # ကုဒ်စတိုင်ပြဿနာများကို စစ်ဆေးပါ
node server.js     # အမှားများမရှိဘဲ ဆာဗာစတင်သည်ကို သေချာစစ်ဆေးပါ
```

### General Testing Approach

- ဒေတာဗေ့စ်သည် အလိုအလျောက် စမ်းသပ်မှု ပုံမှန် မပါဝင်သော ပညာရေးစနစ်ဖြစ်သည်
- စမ်းသပ်မှုများကို လက်မှုပုံစံဖြင့် အောက်ပါအတိုင်း အာရုံစိုက်ပါသည် -
  - ကုဒ်နမူနာများ အမှားမဖြစ်စေဘဲ ပြေးပါခြင်း
  - စာရွက်စာတမ်းတွင် မျှဝေထားသော လင့်ခ်များ အလုပ်လုပ်ရခြင်း
  - ပရောဂျက်တည်ဆောက်မှု ပြီးမြောက်ခြင်း
  - နမူနာများသည် ကောင်းမွန်သော လေ့လာမှုနည်းလမ်းများကို လိုက်နာခြင်း

### Pre-submission Checks

- package.json ပါဝင်သော ဖိုလ်ဒါများတွင် `npm run lint` ကို တင်သတ်ပါ
- markdown လင့်ခ်များကို မှန်ကန်ပြည့်စုံကြောင်း အတည်ပြုပါ
- ဘရောက်ဇာ နှင့် Node.js တို့တွင် ကုဒ်နမူနာများကို စမ်းသပ်ပါ
- ဘာသာပြန်မှုများ၏ ဖွဲ့စည်းမှု မြောက်မြားမှု ထိန်းသိမ်းထားမှု စိစစ်ပါ

## Code Style Guidelines

### JavaScript

- ခေတ်မီ ES6+ စာရေးနည်းကို အသုံးပြုပါ
- ပရောဂျက်အတွင်း ပါရှိသည့် standard ESLint ပြဿနာစနစ်ကို လိုက်နာပါ
- ပညာရေး ရည်ရွယ်ချက်အတွက် သီးခြား နာမည်များ အသုံးပြုပါ
- လေ့လာသူများအတွက် အဓိပ္ပာယ်ဖွင့်ရှင်းချက်များ စာသားတွေ ထည့်ပါ
- Prettier ဖြင့် ပုံစံ စနစ်တကျ ပြုပြင်ထားပါ (configured ရှိလျှင်သာ)

### HTML/CSS

- Semantic HTML5 element များအသုံးပြုခြင်း
- တုန့်ပြန်မှု ဒီဇိုင်း များကို ဆောင်ရွက်ခြင်း
- Class နာမည်များကို ရှင်းလင်းသတိပြုအသုံးပြုပါ
- CSS နည်းကျများအတွက် သင်ယူသူများအတွက် ရှင်းလင်းရေးသားချက်များ ထည့်ပါ

### Python

- PEP 8 စံချိန်စံညွှန်းများ လိုက်နာပါ
- တိကျမြောက်မရှိ ပညာရေးကုဒ်နမူနာများ
- သင်ယူမှု အတွက် အကူအညီဖြစ်စေသည့် Type hints များထည့်ပါ

### Markdown Documentation

- ခေါင်းစဥ် အဆင့်လိုက် ရှင်းလင်းမှု
- ဝါကျဘာသာပြန်ထားသော ကုဒ် ဘလော့တွေ
- အသေးစိတ် ရင်းမြစ်များအတွက် လင့်ခ်များ
- `images/` ဖိုလ်ဒါများတွင် ပုံရိပ်များနှင့် စာရင်းများ
- ရှာဖွေသူများအတွက် ပုံများ၏ Alt စာသားများ

### File Organization

- သင်ခန်းစာများ ကို နံပါတ်လိုက် စီစဉ်ထား (1-getting-started-lessons, 2-js-basics, စသည်)
- ပရောဂျက်တစ်ခုချင်းစီတွင် `solution/` နှင့် တခုခုသော `start/` သို့မဟုတ် `your-work/` ဖိုလ်ဒါများပါဝင်သည်
- ပုံရိပ်များသည် သင်ခန်းစာအလိုက် `images/` ဖိုလ်ဒါများတွင် သိမ်းဆည်းထားသည်
- ဘာသာပြန်ထားသော ဖိုင်များကို `translations/{language-code}/` ဖိုလ်ဒါတွင် သိမ်းဆည်းထားသည်

## Build and Deployment

### Quiz App Deployment (Azure Static Web Apps)

quiz-app သည် Azure Static Web Apps အဆောက်အအုံအတွက် ဆက်တင်ပြုလုပ်ထားသည် -

```bash
cd quiz-app
npm run build      # dist/ အဖိုင်ထည် ဆောက်သည်
# main ထိ တင်သွင်းသောအခါ GitHub Actions workflow ဖြင့် တင်စစ်သည်။
```

Azure Static Web Apps ဆက်တင်များ:
- **App ရှေ့နေရာ**: `/quiz-app`
- **အထွက် ရှေ့နေရာ**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Documentation PDF Generation

```bash
npm install                    # docsify-to-pdf ကို ထည့်သွင်းပါ
npm run convert               # docs မှ PDF ကို ထုတ်လုပ်ပါ
```

### Docsify Documentation

```bash
npm install -g docsify-cli    # Docsify ကို ကမ္ဘာလုံးဆိုင်ရာ ထည့်သွင်းပါ
docsify serve                 # localhost:3000 တွင် ဝန်ဆောင်မှုပေးပါ
```

### Project-specific Builds

ပရောဂျက် တစ်ခုချင်းစီ၏ build လုပ်ငန်းစဉ်သည် မတူကွဲပြားနိုင်ပါသည် -
- Vue ပရောဂျက်များ: `npm run build` နှင့် production bundle များ ဖန်တီးသည်
- Static ပရောဂျက်များ: build လုပ်ခြင်းမရှိဘဲ ဖိုင်များကို တိုက်ရိုက် ဝန်ဆောင်မှု ပြုလုပ်သည်

## Pull Request Guidelines

### Title Format

ပြင်ဆင်ချက် အကွာအဝေးပြသနိုင်စေရန် ခေါင်းစဉ်များကို ရှင်းလင်းဖော်ပြပါ:
- `[Quiz-app] သင်ခန်းစာ X အတွက် စာမေးပွဲ အသစ် ထည့်သွင်းပါ`
- `[Lesson-3] Terrarium ပရောဂျက်တွင် သိပ်ချောင်းမှုတစ်ခု ပြင်ဆင်သည်`
- `[Translation] သင်ခန်းစာ 5 အတွက် စပိန်ဘာသာပြန် ထည့်သွင်းပါ`
- `[Docs] အဆင်ပြေမှု နည်းလမ်းညွှန်ချက် များ ထပ်မံ ပြင်ဆင်ပါ`

### Required Checks

PR တင်မတိုင်မီ လူအတတ်ဆုံး စစ်ဆေးမှုများ -

1. **ကုဒ်အရည်အသွေး**:
   - ဒဏ်ရာရှိသော ပရောဂျက် ဖိုလ်ဒါများတွင် `npm run lint` ထည့်ပြေးပါ
   - lint အမှားများနှင့် သတိပေးချက်များအားလုံး ပြင်ဆင်သည်

2. **Build အတည်ပြုမှု**:
   - မည်သည့် အခါတွင်မဆို `npm run build` ကို ပြေးပါ
   - Build အမှား မရှိကြောင်း သေချာစေပါ

3. **လင့်ခ် စစ်ဆေးမှု**:
   - Markdown လင့်ခ်များအားလုံးကို စမ်းသပ်ပါ
   - ပုံရိပ်ကိုင်တွယ်မှုများ ကို စစ်ဆေးပါ

4. **အကြောင်းအရာ ပြန်လည်သုံးသပ်မှု**:
   - စာလုံးပေါင်းနှင့် အသံဖွဲ့မှု စစ်ဆေးပါ
   - ကုဒ် နမူနာများ မှန်ကန်ပြီး ပညာရေးအတွက်သင့်တော်သည်ကို သေချာစေပါ
   - ဘာသာပြန်မှုများသည် မူရင်း အဓိပ္ပါယ်ကို ထိန်းသိမ်းထားသည်ကို အတည်ပြုပါ

### Contribution Requirements

- Microsoft CLA (အသစ် PR အတွက် အလိုအလျောက် စစ်ဆေးမှု) ပေးအပ်ရန် သဘောတူပါရန်
- [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/) ကို လိုက်နာပါ
- အသေးစိတ် လမ်းညွှန်မှုအတွက် [CONTRIBUTING.md](./CONTRIBUTING.md) ဖတ်ရှုပါ
- PR ဖေါ်ပြချက်တွင် ဆိုင်သော ပြဿနာအမှတ်များ ကို ပြုလုပ်ပါ

### Review Process

- PR များကို မိမိ ဦးဆောင်သူများ နှင့် အသိုင်းအဝိုင်းက ရှင်းလင်း ပြန်လည်သုံးသပ်သည်
- ပညာရေး အပြည့်အဝ ရနိုင်ရေးကို ဦးစားပေးသည်
- ကုဒ် နမူနာများသည် လက်ရှိ အကောင်းဆုံးနည်းလမ်းများနှင့် ကိုက်ညီရမည်
- ဘာသာပြန်မှုများကို တိကျမှုနဲ့ ယဉ်ကျေးမှုသဘောထား အရ အကဲဖြတ်သည်

## Translation System

### Automated Translation

- GitHub Actions နှင့် co-op-translator workflow ကို အသုံးပြုသည်
- ဘာသာစကား ၅၀ ကျော်သို့ အလိုအလျောက် ဘာသာပြန်ပေးသည်
- မူရင်းဖိုင်များကို မူရင်း ဖိုလ်ဒါများတွင် တင်ရှိသည်
- ဘာသာပြန်သော ဖိုင်များကို `translations/{language-code}/` ကုဒ်လမ်းကြောင်းတွင်ထားသည်

### Adding Manual Translation Improvements

1. `translations/{language-code}/` ဖိုလ်ဒါအတွင်း ဖိုင်ရှာဖွေပါ
2. ဖွဲ့စည်းမှု မဖျက်ဆီးဘဲ တိုးတက်အောင် ပြင်ဆင်ပါ
3. ကုဒ်နမူနာများ အလုပ်လုပ်နိုင်မှု ထိန်းသိမ်းပါ
4. ဒေသဆိုင်ရာ စာမေးပွဲအကြောင်းအရာများ တင်ပြပါ

### Translation Metadata

ဘာသာပြန်ထားသော ဖိုင်များတွင် metadata ခေါင်းစီးပါရှိသည် -
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## Debugging and Troubleshooting

### Common Issues

**Quiz app မသွင်းနိုင်သော ပြဿနာ**:
- Node.js ဗားရှင်း (v14+ ဟု အကြံပြု)
- `node_modules` နှင့် `package-lock.json` ဖိုင်များ ဖျက်ပြီး `npm install` ပြန်ပြုလုပ်ပါ
- Port မတူညီမှု (Vite ၏ ပုံမှန် port သည် 5173)

**API server မတက်နိုင်ခြင်း**:
- Node.js ဗားရှင်း (node >=10) ကို အတည်ပြုပါ
- Port သုံးပြီးသားရှိမရှိ စစ်ဆေးပါ
- မလိုအပ်သည့် package များ install လုပ်ထားမရှိကြောင်း စစ်ဆေးပါ

**Browser extension မရောက်ရှိခြင်း**:
- manifest.json ကို မှန်ကန်စွာ စနစ်တကျ ဖန်တီးထားမှု စစ်ဆေးပါ
- Browser console အမှားများ စစ်ဆေးပါ
- Browser-specific extension တပ်ဆင်ခြင်း လမ်းညွှန်ချက်များလိုက်နာပါ

**Python chat project ပြဿနာများ**:
- OpenAI package ကို တပ်ဆင်ထားမှုရှိ/မရှိ စစ်ဆေးပါ `pip install openai`
- GITHUB_TOKEN environment variable ကို သတ်မှတ်ထားမှု ချက်ချင်းစစ်ဆေးပါ
- GitHub Models သုံးခွင့်ရှိမှုကို အတည်ပြုပါ

**Docsify စာရွက်စာတမ်း မပေးနိုင်မှု**:
- docsify-cli ကို ဘောလုံးအဆင့် တပ်ဆင်ပါ `npm install -g docsify-cli`
- ဒေတာဗေ့စ် root ဖိုလ်ဒါမှ ကြိုးစားပြေးပါ
- `docs/_sidebar.md` ဖိုင် ရှိမှုကို စစ်ဆေးပါ

### Development Environment Tips

- HTML ပရောဂျက်များအတွက် VS Code Live Server အက်စတင်းရှင်းအသုံးပြုပါ
- မျှတသော format ဖြင့်ရေးသားရန် ESLint နှင့် Prettier extension များ ထည့်သွင်းပါ
- JavaScript debugging အတွက် browser DevTools သုံးပါ
- Vue ပရောဂျက်များအတွက် Vue DevTools browser extension ထည့်သွင်းပါ

### Performance Considerations

- ဘာသာပြန်ဖိုင် နေရာအများစုသောကြောင့် (ဘာသာစကား ၅၀+) လုံးဝ clone လုပ်ရာတွင် များစွာဖိုင်များ ဖြစ်ပေါ်နိုင်သည်
- အကြောင်းအရာ အလျင်အမြန် ရယူရန် `git clone --depth 1` ကို အသုံးပြုပါ
- ဗမာဘာသာ အကြောင်းအရာများတွင် သင်တန်းသား content တွင် ဘာသာပြန်ဖိုင်များကို ရှာဖွေရန် မထည့်ပါနှင့်
- npm install နှင့် Vite build တို့ကဲ့သို့ build လုပ်ဆောင်မှုများ ပထမအကြိမ် run မှာ နှေးကွေးဖြစ်တတ်ပါသည်

## Security Considerations

### Environment Variables

- API key များကို ဒေတာဗေ့စ် သို့ မှတ်သား မထားသင့်ပါ
- `.env` ဖိုင်များ အသုံးပြုပါ ( `.gitignore` ထဲမှာ ရှိပြီး)
- သက်ဆိုင်ရာ ပရောဂျက် README များတွင် လိုအပ်သည့် environment variables များ ဖော်ပြထားပါ

### Python Projects

- Virtual environment အသုံးပြုပါ: `python -m venv venv`
- dependency များကို Update လုပ်ထားပါ
- GitHub tokens များကို လိုအပ်သည့် ခွင့်ပြုချက် နည်းဆုံး သတ်မှတ်ပါ

### GitHub Models Access

- GitHub Models သုံးရန် Personal Access Tokens (PAT) လိုအပ်ပါသည်
- tokens များကို environment variables အဖြစ် လျှို့ဝှက်ထားပါ
- tokens သို့မဟုတ် စကားဝှက်များကို မည်သည့်အချိန်တွင်မဆို commit မပြုလုပ်ရပါ

## Additional Notes

### Target Audience

- ဝဘ်ဒီဗလပ်မှန်အခြေခံသူ အသစ်စိတ် ပြုလုပ်သူများ
- ကျောင်းသားများနှင့် ကိုယ်တိုင်လေ့လာသူများ
- သင်တန်းကျောင်းများ၌ သင်ကြားသူများ
- ဤ content များသည် လွယ်ကူမြန်ဆန် ရှဉ့်ချိန်နှင့် အဆင့်လိုက်ကျွမ်းကျင်မှုတိုးတက်စေခြင်းအတွက် အထူးပြု ဒီဇိုင်းဖြစ်သည်

### Educational Philosophy

- စီမံကိန်း အခြေပြု သင်ကြားမှု နည်းလမ်း
- မကြာခဏ ဉာဏ်စမ်း စစ်ဆေးမှုများ (စာမေးပွဲများ)
- လက်တွေ့ ကုဒ် ရေးခွင့်များ
- လက်တွေ့ ကမ္ဘာဆိုင်ရာ အသုံးချမှု နမူနာများ
- Framework မတိုင်မှီ အခြေခံကို အားပေးခြင်း

### Repository Maintenance

- လေ့လာသင်ယူသူများနှင့် ဆောင်ရွက်သူများ စည်းလုံးညီညွတ်မှုရှိ
- အမြဲတမ်း dependency လေးစားမှု နှင့် အကြောင်းအရာ အပ်ဒိတ်များ
- ပြဿနာများနှင့် ဆွေးနွေးမှုများကို maintainers က ထိန်းသိမ်းကြည့်ရှု
- ဘာသာပြန်မှုများကို GitHub Actions ဖြင့် အလိုအလျောက် ပြုလုပ်သည်

### Related Resources

- [Microsoft Learn modules](https://docs.microsoft.com/learn/)
- [Student Hub resources](https://docs.microsoft.com/learn/student-hub/)
- သင်ယူသူများအတွက် အကြံပြုချက် - [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- အပို သင်တန်းများ: Generative AI, Data Science, ML, IoT သင်ရိုးညွှန်းလမ်းကြောင်းများ ရရှိနိုင်သည်

### Working with Specific Projects

အသေးစိတ် လမ်းညွှန်ချက်များအတွက် အောက်ဖော်ပြပါ README ဖိုင်များကို ကြည့်ပါ -
- `quiz-app/README.md` - Vue 3 quiz application
- `7-bank-project/README.md` - Banking application with authentication
- `5-browser-extension/README.md` - Browser extension development
- `6-space-game/README.md` - Canvas-based game development
- `9-chat-project/README.md` - AI chat assistant project

### Monorepo Structure

ဤဒေတာဗေ့စ်သည် ပုံမှန် Monorepo မဟုတ်ပေမဲ့ အဓိက တစ်နေရာတည်းတွင် ပရောဂျက်များစွာ ရှိပါသည် -
- သင်ခန်းစာ တစ်ခုချင်းစီ သီးခြားဖြစ်သည်
- ပရောဂျက်များသည် dependency များ မမျှဝေပါ
- တစ်ခုချင်းပရောဂျက်များအပေါ် လုပ်ကိုင်ရန် မတူညီသော အတွေ့အကြုံ မပျက်စီးပါ
- စတင်လေ့လာမှုအတွက် ဒေတာဗေ့စ် အားလုံး clone လုပ်ပါ

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**ကြေညာချက်**:  
ဤစာတမ်းကို AI ဘာသာပြန်ခြင်းဝန်ဆောင်မှု [Co-op Translator](https://github.com/Azure/co-op-translator) မှ အသုံးပြုပြီး ဘာသာပြန်ထားပါသည်။ ကျွန်ုပ်တို့သည် တိကျမှုအတွက် ကြိုးပမ်းနေသော်လည်း၊ အလိုအလျောက် ဘာသာပြန်ချက်များတွင် အမှားများ သို့မဟုတ် တိကျမှု လျော့နည်းချက်များ ရှိနိုင်သည်ကို သတိပြုပါ။ မူရင်းစာတမ်းကို မူရင်းဘာသာဖြင့်သာ စံချိန်စံညွှန်းအားဖြင့် သတ်မှတ်သင့်ပါသည်။ အရေးကြီးသော အချက်အလက်များအတွက်တော့ ပညာရှင်လူ့ဘာသာပြန်ခြင်းကို အကြံပြုပါသည်။ ဤဘာသာပြန်ချက် အသုံးပြုမှုကြောင့် ဖြစ်ပေါ်နိုင်သည့် မတိကျမှုများ သို့မဟုတ် နားမလည်မှုများအတွက် ကျွန်ုပ်တို့၏ တာဝန်မရှိပါကြောင်း အသိပေးအပ်ပါသည်။
<!-- CO-OP TRANSLATOR DISCLAIMER END -->
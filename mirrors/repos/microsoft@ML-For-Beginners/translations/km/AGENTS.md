# AGENTS.md

## Project Overview

នេះគឺជាឯកសារ **ការសិក្សា ម៉ាស៊ីនរៀនសម្រាប់អ្នកចាប់ផ្តើម** ដែលមានកម្មវិធីសិក្សាប្រមាណ ១២ សប្ដាហ៍ មានមេរៀន ២៦ មេរៀនគ្របដណ្តប់គំនិតម៉ាស៊ីនរៀនបុរាណ ដោយប្រើ Python (ជាសំខាន់ជាមួយ Scikit-learn) និង R។ ឃ្លាំងទាក់ទងនេះត្រូវបានរចនាឡើងជាឋានសិក្សាដោយខ្លួនឯង មានគម្រោងដៃ អ្នកសាកល្បង និងការងារសិក្សា រៀងរាល់មេរៀនស្វែងយល់ពីមូលដ្ឋាន ML តាមរយៈទិន្នន័យពិតពីវប្បធម៌ និងតំបន់ផ្សេងៗជុំវិញពិភពលោក។

ធាតុសំខាន់ៗ៖
- **មាតិកាសិក្សា**៖ ២៦ មេរៀនគ្របដណ្តប់ការណែនាំអំពី ML, ការត្រួតពិនិត្យទំនាក់ទំនង, ការបែងចែកចំណាត់ថ្នាក់, ការបែងចែកក្រុម, NLP, លំដាប់ពេលវេលា និងការរៀនពង្រឹង
- **កម្មវិធីសាកល្បង**៖ កម្មវិធីសាកល្បងមួយបង្កើតជាមួយ Vue.js មានការវាស់ថ្នាក់មុន និងក្រោយមេរៀន
- **គាំទ្រភាសាច្រើន**៖ បម្លែងភាសាឡើងវិញដោយស្វ័យប្រវត្តិទៅជាភាសាបានជាង ៤០ ភាសាតាមរយៈ GitHub Actions
- **គាំទ្រភាសាគូ**៖ មេរៀនអាចប្រើបានទាំង Python (សៀវភៅកិច្ចការលើ Jupyter) និង R (ឯកសារ R Markdown)
- **ការសិក្សាដើមឯកសារ**៖ រៀងរាល់ប្រធានបទមានគម្រោង និងការងារអនុវត្ត

## Repository Structure

```
ML-For-Beginners/
├── 1-Introduction/         # ML basics, history, fairness, techniques
├── 2-Regression/          # Regression models with Python/R
├── 3-Web-App/            # Flask web app for ML model deployment
├── 4-Classification/      # Classification algorithms
├── 5-Clustering/         # Clustering techniques
├── 6-NLP/               # Natural Language Processing
├── 7-TimeSeries/        # Time series forecasting
├── 8-Reinforcement/     # Reinforcement learning
├── 9-Real-World/        # Real-world ML applications
├── quiz-app/           # Vue.js quiz application
├── translations/       # Auto-generated translations
└── sketchnotes/       # Visual learning aids
```

ថតមេរៀនរៀងរាល់មេរៀនធម្មតានឹងមាន៖
- `README.md` - មាតិកាមេរៀនសំខាន់
- `notebook.ipynb` - សៀវភៅកិច្ចការចេញពី Jupyter Python
- `solution/` - កូដដំណោះស្រាយ (Python និង R)
- `assignment.md` - លំហាត់អនុវត្ត
- `images/` - ឯកសារទ្រព្យសម្បត្តិរូបភាព

## Setup Commands

### For Python Lessons

មេរៀនភាគច្រើនប្រើសៀវភៅកិច្ចការជាមួយ Jupyter។ តំឡើងអ្វីដែលត្រូវការ៖

```bash
# តំឡើង Python 3.8+ ប្រសិនបើមិនបានតំឡើងរួចជាមុន
python --version

# តំឡើង Jupyter
pip install jupyter

# តំឡើងបណ្ណាល័យ ML រួមៗ
pip install scikit-learn pandas numpy matplotlib seaborn

# សម្រាប់មេរៀនជាក់លាក់ សូមពិនិត្យតម្រូវការជាក់លាក់សម្រាប់មេរៀននោះ
# ឧទាហរណ៍៖ មេរៀនកម្មវិធីវេប
pip install flask
```

### For R Lessons

មេរៀន R ស្ថិតក្នុងថត `solution/R/` ជាឯកសារ `.rmd` ឬ `.ipynb`៖

```bash
# ដំឡើង R និងកញ្ចប់ដែលត្រូវការ
# នៅក្នុងកុងសូល R:
install.packages(c("tidyverse", "tidymodels", "caret"))
```

### For Quiz Application

កម្មវិធីសាកល្បងគឺនូវកម្មវិធី Vue.js ដែលស្ថិតនៅថត `quiz-app/`៖

```bash
cd quiz-app
npm install
```

### For Documentation Site

ដើម្បីរត់គេហទំព័រឯកសារនៅក្នុងម៉ាស៊ីនកុំព្យូទ័រ៖

```bash
# ដំឡើង Docsify
npm install -g docsify-cli

# សេវាកម្មពីឫសហាងស្តុក
docsify serve

# ចូលប្រើនៅ http://localhost:3000
```

## Development Workflow

### Working with Lesson Notebooks

១. ទៅកាន់ថតមេរៀន (ឧ. `2-Regression/1-Tools/`)
២. បើកសៀវភៅកិច្ចការជា Jupyter:
   ```bash
   jupyter notebook notebook.ipynb
   ```

៣. ធ្វើខ្សែសំរាប់កម្រិតមេរៀននិងលំហាត់
៤. ពិនិត្យដំណោះស្រាយក្នុងថត `solution/` ប្រសិនបើចាំបាច់

### Python Development

- មេរៀនប្រើបណ្ណាល័យវិទ្យាសាស្ដ្រទិន្នន័យ Python ស្តង់ដារ
- សៀវភៅកិច្ចការជា Jupyter សម្រាប់សិក្សាផ្ទាល់
- កូដដំណោះស្រាយមានក្នុងថត `solution/` រាល់មេរៀន

### R Development

- មេរៀន R មានទ្រង់ទ្រាយ `.rmd` (R Markdown)
- ដំណោះស្រាយស្ថិតនៅក្នុងថត `solution/R/`
- ប្រើ RStudio ឬ Jupyter ជាមួយកឺណែល R ដើម្បីរត់សៀវភៅ R

### Quiz Application Development

```bash
cd quiz-app

# ចាប់ផ្តើមម៉ាស៊ីនមេអភិវឌ្ឍន៍
npm run serve
# ចូលប្រើនៅ http://localhost:8080

# សាងសង់សម្រាប់ផលិតកម្ម
npm run build

# ពិនិត្យនិងជួសជុលឯកសារ
npm run lint
```

## Testing Instructions

### Quiz Application Testing

```bash
cd quiz-app

# ពិនិត្យកូដ
npm run lint

# សង់ដើម្បីផ្ទៀងផ្ទាត់ថាមិនមានកំហុសណាមួយ
npm run build
```

**Note**: នេះគឺជាឃ្លាំងមេរៀនសំរាប់ការអប់រំបំផុត។ គ្មានការធ្វើតេស្តស្វ័យប្រវត្តិសម្រាប់មាតិកាមេរៀនទេ។ ការផ្ទៀងផ្ទាត់ត្រូវបានធ្វើតាម៖
- បញ្ចប់លំហាត់មេរៀន
- រត់កោដ្ឋ Jupyter ឲ្យបានជោគជ័យ
- ពិនិត្យលទ្ធផលអោយទៅតាមការរំពឹងទុកក្នុងដំណោះស្រាយ

## Code Style Guidelines

### Python Code
- បន្ទាប់បន្សាំនូវគន្លង PEP 8
- ប្រើឈ្មោះអថេរបញ្ជាក់ច្បាស់
- កំណត់សំគាល់សម្រាប់ដំណើរការលំបាក
- សៀវភៅ Jupyter ត្រូវមានកោដ្ឋ markdown សំរាប់ពន្យល់គំនិត

### JavaScript/Vue.js (Quiz App)
- គោរពតាមម៉ូដែល Vue.js
- ការកំណត់ ESLint នៅក្នុង `quiz-app/package.json`
- រត់ `npm run lint` ដើម្បីពិនិត្យ និងជួសជុលបញ្ហា

### Documentation
- ឯកសារ markdown គួរតែល្អ និងមានរចនាសម្ព័ន្ធល្អ
- រួមបញ្ចូលខេនដេមកូដនៅក្នុងប្រអប់បិទបើក
- ប្រើតំណភ្ជាប់ទាក់ទងសម្រាប់យោងខាងក្នុង
- គោរពទ្រង់ទ្រាយដែលមានរួចជាមុន

## Build and Deployment

### Quiz Application Deployment

កម្មវិធីសាកល្បងអាចប្រើបានក្នុង Azure Static Web Apps៖

១. **លក្ខខណ្ឌមុន**៖
   - គណនី Azure
   - ឃ្លាំង GitHub (បាន fork រួច)

២. **បញ្ចូនទៅ Azure**៖
   - បង្កើតធនធាន Azure Static Web App
   - ភ្ជាប់ទៅឃ្លាំង GitHub
   - កំណត់ទីតាំងកម្មវិធី: `/quiz-app`
   - កំណត់ទីតាំងលទ្ធផល: `dist`
   - Azure បង្កើត GitHub Actions workflow ដោយស្វ័យប្រវត្តិ

៣. **GitHub Actions Workflow**៖
   - គំនិតកម្មវិធី workflow នៅ `.github/workflows/azure-static-web-apps-*.yml`
   - បង្កើត និងដាក់ចេញស្វ័យប្រវត្តិពេល push ទៅផ្នែក main

### Documentation PDF

បង្កើត PDF ពីឯកសារអ្នកតាំង៖

```bash
npm install
npm run convert
```

## Translation Workflow

**សំខាន់**៖ ការប្រែបកបម្លែងនៅតែបន្តដោយស្វ័យប្រវត្តិតាមរយៈ GitHub Actions ប្រើកម្មវិធី Co-op Translator។

- ការប្រែបកបម្លែងបានបង្កើតឡើងដោយស្វ័យប្រវត្តិពេលមានការផ្លាស់ប្តូរនៅផ្នែក `main`
- **សូមមិន​ប្រែទាំងអស់ដោយដៃ** - ប្រព័ន្ធបានដោះស្រាយនេះ
- កម្មវិធី workflow មាននៅ `.github/workflows/co-op-translator.yml`
- ប្រើសេវា AI/OpenAI របស់ Azure សម្រាប់បកប្រែ
- គាំទ្រភាសាជាង ៤០

## Contributing Guidelines

### For Content Contributors

១. **ធ្វើ fork** ឃ្លាំងហើយបង្កើតសាខាកំណត់ឡើងវិញ
២. **បង្កើតការផ្លាស់ប្តូរមេរៀន** ប្រសិនបើបន្ថែម/ធ្វើបច្ចុប្បន្នភាពមេរៀន
៣. **កុំដូរ ឯកសារប្រែ** - ពួកវាត្រូវបានបង្កើតស្វ័យប្រវត្តិ
៤. **ធ្វើតេស្តកូដ** - បញ្ចប់ការរត់នៃកោដ្ឋឲ្យបានជោគជ័យ
៥. **ពិនិត្យតំណភ្ជាប់ និងរូបភាព** ឲ្យបានត្រឹមត្រូវ
៦. **ដាក់ស្នើ pull request** ជាមួយការពិពណ៌នាច្បាស់លាស់

### Pull Request Guidelines

- **ទ្រង់ទ្រាយចំណងជើង**៖ `[ផ្នែក] សេចក្ដីពិពណ៌នាខ្លីអំពីការផ្លាស់ប្តូរ`
  - ឧ.៖ `[Regression] កែសម្រួលកំហុសពាក្យនៅមេរៀនលេខ ៥`
  - ឧ.៖ `[Quiz-App] បច្ចុប្បន្នភាពអស់កល្បជំនួយ`
- **មុនដាក់ស្នើ**៖
  - ឆែកថាឲ្យកោដ្ឋ Jupyter រត់បានទាំងអស់ដោយគ្មានកំហុស
  - រត់ `npm run lint` ប្រសិនបើកែប្រែកម្មវិធីសាកល្បង
  - ពិនិត្យទ្រង់ទ្រាយ markdown
  - សាកល្បងឧទាហរណ៍កូដថ្មីៗ
- **PR ត្រូវមាន**៖
  - ពិពណ៌នាអំពីការផ្លាស់ប្តូរ
  - ហេតុផលនៃការផ្លាស់ប្តូរ
  - រូបថតផ្ទាំងពេល UI ផ្លាស់ប្តូរ
- **Code of Conduct**៖ គោរពតាម [Microsoft Open Source Code of Conduct](CODE_OF_CONDUCT.md)
- **CLA**៖ អ្នកត្រូវចុះហត្ថបទ Contributor License Agreement

## Lesson Structure

រៀងរាល់មេរៀនមានលំនាំដូចតទៅ៖

១. **សាកល្បងមុនបង្ហាញមេរៀន** - តេស្តចំណេះដឹងមូលដ្ឋាន
២. **មាតិកាមេរៀន** - វិធានការនិងពណ៌នាច្បាស់លាស់
៣. **ការបង្ហាញកូដ** - ឧទាហរណ៍អនុវត្តក្នុងសៀវភៅកិច្ចការចេញពីសៀវភៅ
៤. **ការត្រួតពិនិត្យចំណេះដឹង** - បញ្ជាក់ការយល់ដឹងរបស់អ្នកសិក្សា
៥. **សកម្មភាពប défi** - អនុវត្តគំនិតដោយឯករាជ្យ
៦. **ការងារសិក្សា** - លំហាត់បន្ថែម
៧. **សាកល្បងក្រោយបង្ហាញមេរៀន** - វាស់តម្លៃលទ្ធផលការសិក្សា

## Common Commands Reference

```bash
# Python/Jupyter
jupyter notebook                    # ចាប់ផ្តើមម៉ាស៊ីនបម្រើ Jupyter
jupyter notebook notebook.ipynb     # បើកសៀវភៅកំណត់សម្រាប់ជាក់លាក់
pip install -r requirements.txt     # ដំឡើង依赖项 (នៅពេលមាន)

# កម្មវិធីសំណួរ
cd quiz-app
npm install                        # ដំឡើង依赖项
npm run serve                      # ម៉ាស៊ីនបម្រើអភិវឌ្ឍន៍
npm run build                      # សង់ការផលិត
npm run lint                       # ពិនិត្យនិងជួសជុលកូដ

# ឯកសារ
docsify serve                      # បម្រើឯកសារនៅលើម៉ាស៊ីនដំណើរការផ្ទាល់
npm run convert                    # បង្កើតឯកសារ PDF

# ដំណើរការការងារ Git
git checkout -b feature/my-change  # បង្កើតសាខាឯកសារ
git add .                         # រៀបចំការផ្លាស់ប្ដូរ
git commit -m "Description"       # ប្តឹងការផ្លាស់ប្ដូរ
git push origin feature/my-change # ទំនាក់ទំនងទៅពីចម្ងាយ
```

## Additional Resources

- **Microsoft Learn Collection**: [ម៉ូឌុល ML សម្រាប់អ្នកចាប់ផ្តើម](https://learn.microsoft.com/en-us/collections/qrqzamz1nn2wx3?WT.mc_id=academic-77952-bethanycheum)
- **កម្មវិធីសាកល្បង**: [ការសាកល្បងអនឡាញ](https://ff-quizzes.netlify.app/en/ml/)
- **ពិភាក្សាជួយគ្នា**: [GitHub Discussions](https://github.com/microsoft/ML-For-Beginners/discussions)
- **វីដេអូមើលឆ្លងកាត់**: [Playlists YouTube](https://aka.ms/ml-beginners-videos)

## Key Technologies

- **Python**: ភាសាសំខាន់សម្រាប់មេរៀន ML (Scikit-learn, Pandas, NumPy, Matplotlib)
- **R**: ជម្រើសផ្សេងក្នុងការប្រើ tidyverse, tidymodels, caret
- **Jupyter**: សៀវភៅកិច្ចការផ្លូវចូលសម្រាប់មេរៀន Python
- **R Markdown**: ឯកសារសម្រាប់មេរៀន R
- **Vue.js 3**: ស៊ុមកម្មវិធីសាកល្បង
- **Flask**: ស៊ុមកម្មវិធីតំបន់វេបសម្រាប់ដាក់ម៉ូដែល ML
- **Docsify**: កម្មវិធីបង្កើតគេហទំព័រកម្រងឯកសារ
- **GitHub Actions**: CI/CD និងការប្រែបកស្វ័យប្រវត្តិ

## Security Considerations

- **គ្មានសម្ងាត់ក្នុងកូដ**: មិនបណ្តេញ API key ឬស្នាក់ហេតុវិញ
- **ការពឹងផ្អែក**: រក្សាឲ្យ npm និង pip ឡើងវិញជានិច្ច
- **ការបញ្ចូលអ្នកប្រើ**: ឧទាហរណ៍វេប Flask មានការត្រួតពិនិត្យ input មូលដ្ឋាន
- **ទិន្នន័យរបស់អ្នកប្រើ**: ឧទាហរណ៍ទិន្នន័យពេញចិត្ត និងមិនសំខាន់

## Troubleshooting

### Jupyter Notebooks

- **បញ្ហាគឺណែល**: ចាប់ផ្តើមឡើងវិញ kernel ប្រសិនបើកោដ្ឋអង្គភាពផ្អាក: Kernel → Restart
- **បញ្ហានាំចូល**: ច្បាស់ថាមិនខ្វះការដំឡើងបណ្ណាល័យជាមួយ pip
- **បញ្ហាផ្លូវការដំណើរការ**: រត់សៀវភៅពីថតមេរបស់វា

### Quiz Application

- **npm install បរាជ័យ**: សម្អាត cache npm: `npm cache clean --force`
- **ប្រហោង port ប្រកែក**: ផ្លាស់ប្តូរប្រហោងជាមួយ: `npm run serve -- --port 8081`
- **បញ្ហាការសង់**: លុប `node_modules` ហើយដំឡើងឡើងវិញ: `rm -rf node_modules && npm install`

### R Lessons

- **កញ្ចប់មិនមានជារៀងរាល់ថ្ងៃ**: ដំឡើងជាមួយ: `install.packages("package-name")`
- **ការបម្រុង RMarkdown**: ប្រាកដថាកញ្ចប់ rmarkdown ត្រូវបានដំឡើង
- **បញ្ហាគឺណែល**: អាចត្រូវដំឡើង IRkernel សម្រាប់ Jupyter

## Project-Specific Notes

- នេះជាកម្មវិធីសិក្សាទូទៅ មិនមែនគឺកូដផលិតកម្ម
- ផ្តោតលើការយល់ដឹងគំនិត ML តាមការអនុវត្តទាំងអស់
- ឧទាហរណ៍កូដផ្តោតលើភាពវចនាធិប្បាយល្អ
- មេរៀនភាគច្រើនមានតែម្ដង ហើយអាចបញ្ចប់ដោយខ្លួនឯង
- បានផ្តល់ដំណោះស្រាយ ប៉ុន្តែអ្នកសិក្សាគួរព្យាយាមលំហាត់ជាមុន
- ឃ្លាំងប្រើ Docsify សម្រាប់បង្កើតគេហទំព័រឯកសារដោយគ្មានដំណើរការសង់
- សេចក្ដីសង្ខេបជារូបភាព (Sketchnotes) ផ្តល់ការពន្យល់យ៉ាងច្បាស់អំពីគំនិត
- គាំទ្រភាសាច្រើនធ្វើឲ្យមាតិកាដំណើរការជាសកល

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**ការជម្រាបជូន**៖  
ឯកសារនេះត្រូវបានបកប្រែដោយប្រើសេវាកម្មបកប្រែ AI [Co-op Translator](https://github.com/Azure/co-op-translator)។ ខណៈពេលយើងខិតខំប្រឹងប្រែងសម្រាប់ភាពត្រឹមត្រូវ សូមកត់សម្គាល់ថាការបកប្រែដោយស្វ័យប្រវត្តិអាចមានកំហុសឬភាពមិនត្រឹមត្រូវខ្លះ។ ឯកសារដើមក្នុងភាសាម្ចាស់ដើមគួរត្រូវបានគេយកសម្រាប់ប្រភពត្រឹមត្រូវជាចម្បង។ សម្រាប់ព័ត៌មានសំខាន់ៗ សូមផ្តល់អនុសាសន៍ការបកប្រែដោយអ្នកជំនាញមនុស្ស។ យើងមិនទទួលខុសត្រូវចំពោះការយល់ច្រឡំ ឬការបកប្រែខុសៗណាមួយ ដែលបណ្តាលមកពីការប្រើប្រាស់ការបកប្រែនេះទេ។
<!-- CO-OP TRANSLATOR DISCLAIMER END -->
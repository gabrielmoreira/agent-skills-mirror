---
name: matlab-train-network
description: >
  Train, evaluate, and deploy neural networks in MATLAB.
  Migrate legacy code (fitnet, patternnet, trainNetwork,
  DAGNetwork) to modern, recommended R2024a+ APIs (trainnet, dlnetwork,
  testnet, imagePretrainedNetwork). Use when training, fine-tuning, evaluating,
  running inference, exporting to Simulink, or converting old training
  scripts.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# matlab-train-network

Train, evaluate, and deploy neural networks in MATLAB using the
recommended `dlnetwork`-based API (`trainnet`, `dlnetwork`, `minibatchpredict`,
`scores2label`, `testnet`, `imagePretrainedNetwork`, `fitcnet`, `fitrnet`).

## When to Use

Activate this skill when a user asks to:

- Train any neural network (classifier, regression, multi-output, LSTM, CNN, etc.)
- Fine-tune or use a pretrained model for transfer learning
- Evaluate a trained network on test data
- Run inference / predict with a trained network
- Export a trained network to Simulink
- Migrate existing legacy deep learning code (trainNetwork, patternnet, fitnet,
  narxnet, gensim) to recommended APIs
- Create a "pattern recognition network", "function fitting network", "NARX
  network", or any task historically associated with the Neural Network Toolbox
  shallow nets API

## When NOT to Use

- Importing/exporting models (importNetworkFromPyTorch, exportONNXNetwork)
- Data loading and preprocessing (imageDatastore, transforms, augmentation)
- Network architecture design decisions (choosing CNN vs LSTM vs transformer)
- Reinforcement learning workflows (use Reinforcement Learning Toolbox)
- Object detection (use specialized detector training functions in Computer Vision Toolbox)

## Decision: fitrnet/fitcnet or trainnet

- **Tabular data?** → `fitrnet` (regression) or `fitcnet` (classification)
- **Tabular data, but need a non-LBFGS solver or a non-MSE/cross-entropy loss?** → `trainnet`
- **Everything else?** → `trainnet`

```matlab
% Classification
mdl = fitcnet(XTrain, TTrain, LayerSizes=20);
[labels,score] = predict(mdl,XTest);
L = loss(mdl, XTest, TTest);

% Regression
mdl = fitrnet(XTrain, TTrain, LayerSizes=[20 20]);
YTest = predict(mdl,XTest);
L = loss(mdl, XTest, TTest);
```

- From R2024b, `fitrnet` supports multi-response variables.
- From R2025a, for custom architectures beyond `LayerSizes`, `Activations`, `LayerWeightsInitializer`, and `LayerBiasesInitializer`, pass a `dlnetwork` via the `Network` name-value argument.

---

## Conventions

### Training with trainnet + dlnetwork

#### Data formats

`trainnet` expects data in specific orientations by default:

| Input layer | Expected data shape |
|-------------|-------------------|
| `featureInputLayer(C)` | observations×channels (e.g., 150×4) |
| `imageInputLayer([H W C])` | H×W×C×observations (e.g., 28×28×1×5000) |
| `sequenceInputLayer(C)` | timesteps×channels×observations, or an observations×1 cell array where each element is a timesteps×channels time series |

If your data has a different layout, use `InputDataFormats` and/or
`TargetDataFormats` in `trainingOptions` instead of transposing the data manually.
The format string describes your data's current layout — one letter per
dimension, not the desired layout. MATLAB handles the remapping internally.
For cell arrays, add `"B"` (batch) to the format string — e.g.,
`InputDataFormats="CTB"` for cells of C×T matrices. Do not specify these
options when data already matches the input layer's default.

#### What trainnet supports

Use `trainnet` and `dlnetwork` for all Deep Learning Toolbox training. This includes:

- Standard classification and regression
- Transfer learning
- Multi-input or multi-output networks
- Custom loss functions (pass a function handle to `trainnet`)
- Custom loss function backward passes via `DifferentiableFunction`
- Custom metrics (string, function handle, or `deep.Metric` subclass)
- Custom stopping criteria via `OutputFcn` in `trainingOptions`
- Custom layers

**Only** use a custom training loop (`dlfeval`/`dlgradient`/update functions) when a
customization is impossible via `trainingOptions` — for example, a custom weight
update rule. Note that `trainingOptions` supports L-BFGS (R2023b+) and
Levenberg-Marquardt `"lm"` (R2024b+).

### NEVER use these legacy APIs

If the user has existing code using these APIs, migrate it to the recommended
replacement and briefly explain which APIs were replaced and what the modern
equivalents are. If the user asks for a legacy API by name, acknowledge their
request and explain that the function has been replaced with a recommended
alternative before providing the solution.

| Legacy API | Recommended replacement |
|-----------|-------------------|
| `trainNetwork` | `trainnet` |
| `patternnet` | `fitcnet` (preferred), or `dlnetwork` + `trainnet` |
| `fitnet` | `fitrnet` (preferred), or `dlnetwork` + `trainnet` |
| `feedforwardnet` | `dlnetwork` + `trainnet` |
| `narxnet`, `timedelaynet` | `nlarx` (preferred), or `dlnetwork` + `trainnet` |
| `train()` (shallow `network` object) | `trainnet` |
| `classify` | `minibatchpredict` + `scores2label` |
| `activations` | `minibatchpredict(net,data,Outputs=layer)` |
| `predictAndUpdateState`, `classifyAndUpdateState` | `[Y, state] = predict(net,X); net.State = state;` |
| `classificationLayer` | Not required — use `trainnet` with `"crossentropy"` as the loss |
| `regressionLayer` | Not required — use `trainnet` with `"mse"` as the loss |
| `DAGNetwork`, `SeriesNetwork`, `layerGraph` | `dlnetwork` — supports `addLayers` and `connectLayers` for multi-branch architectures, anything `layerGraph` can do, `dlnetwork` can do directly |
| `resnet18`, `googlenet`, `squeezenet`, etc. (pretrained network functions that return `DAGNetwork`) | `imagePretrainedNetwork("resnet18", ...)` — returns a `dlnetwork` |
| Manually converting network scores to labels (e.g., `[~,idx] = max(scores)`) | `scores2label` |
| `plotconfusion` | `confusionchart` |
| `gensim` | `exportNetworkToSimulink` (preferred), or Predict block |
| `preparets` | `nlarx` (preferred, handles delays internally), or `dlnetwork` with `sequenceInputLayer(C, MinLength=numDelays)` + `convolution1dLayer(numDelays, ..., Padding="causal")` |
| `closeloop` | `forecast` (preferred, with `nlarx`), or iterative `predict` loop feeding previous predictions back as input |

### Inference — use minibatchpredict (or predict)

- `predict` on a `dlnetwork` accepts plain numeric arrays. Do not wrap inputs
  in `dlarray` or call `extractdata` on outputs.
- For classification: use `minibatchpredict` (or `predict`) + `scores2label`.
- For regression or when you need raw scores: use `minibatchpredict` or `predict`.

### Evaluation — use testnet

- Always use `testnet` for post-training evaluation on a test set.
- For single-output networks, use string metrics: `"accuracy"`, `"rmse"`.
- `trainnet` and `testnet` accept targets as a separate argument only for
  in-memory data. When passing a datastore, targets must be embedded in the
  datastore itself (e.g., labeled imageDatastore or combined datastore with
  targets in a second column) — datastores do not support a separate targets
  argument.
- For multi-output networks or advanced metric customization, see
  `references/metrics-guidance.md`.

### Transfer learning — use imagePretrainedNetwork

- Use `net = imagePretrainedNetwork("squeezenet", NumClasses=5)` — it handles
  layer replacement automatically. The function returns class names only when
  both `NumClasses` and `NumResponses` are unset (pretrained mode). For transfer
  learning, get class names from training data: `categories(imdsTrain.Labels)`.
- Never manually extract `layerGraph`, `replaceLayer`, or add
  `classificationLayer`.

---

## Workflow: Training

### Before choosing a workflow

**Stop and check:** Is your data tabular?

- **Yes** → Use `fitrnet` (regression) or `fitcnet` (classification). See the Decision section above.
- **No** → Use `trainnet` below.

### Standard training

```matlab
% Define network
numChannels = 3;
numClasses = 5;
net = dlnetwork([
    sequenceInputLayer(numChannels)
    lstmLayer(100, OutputMode="last")
    fullyConnectedLayer(numClasses)
    softmaxLayer
]);

% Training options
options = trainingOptions("adam", ...
    MaxEpochs=30, ...
    MiniBatchSize=128, ...
    ValidationData={XVal,TVal}, ...
    Metrics="accuracy", ...
    Plots="training-progress");

% Train
net = trainnet(XTrain,TTrain,net,"crossentropy",options);
```

### Custom loss function for multi-output

The function handle receives network outputs then targets, in order.
Pass categorical targets directly — `trainnet` one-hot encodes them automatically.

```matlab
lossFcn = @(Y1, Y2, T1, T2) crossentropy(Y1,T1) + mse(Y2,T2);

net = trainnet(ds,net,lossFcn,options);
```

For the full multi-output recipe (OutputNames alignment, combined datastores,
testnet evaluation), see `references/multi-output-training.md`.

### Transfer learning

```matlab
net = imagePretrainedNetwork("squeezenet",NumClasses=5);

options = trainingOptions("adam", ...
    MaxEpochs=10, ...
    MiniBatchSize=16, ...
    InitialLearnRate=1e-4, ...
    ValidationData=augimdsVal, ...
    Metrics="accuracy", ...
    Plots="training-progress");

net = trainnet(augimdsTrain,net,"crossentropy",options);

% Inference — class names come from training data
classNames = categories(imdsTrain.Labels);
scores = minibatchpredict(net,XTest);
labels = scores2label(scores,classNames);
```

---

## Workflow: Inference

### Classification

```matlab
scores = minibatchpredict(net,XTest);
labels = scores2label(scores,classNames);
```

### Regression

```matlab
YTest = minibatchpredict(net,XTest);
```

### Single-image or small-batch prediction

```matlab
YPred = predict(net,X);
```

`predict` on `dlnetwork` accepts plain numeric arrays directly. Do not wrap
inputs in `dlarray` or call `extractdata` on outputs.

---

## Workflow: Evaluation

### In-memory data (separate targets)

```matlab
accuracy = testnet(net,XTest,TTest,"accuracy");
rmse = testnet(net,XTest,TTest,"rmse");
```

### Datastores (targets embedded — do NOT pass separate targets)

```matlab
% Labels are already in the datastore — pass only datastore + metric
accuracy = testnet(net,augimdsTest,"accuracy");
```

For multi-output networks or custom metrics, see `references/metrics-guidance.md`.

---

## Workflow: Simulink Deployment

- **Small networks** (all layers supported): use `exportNetworkToSimulink`
- **Large networks**: use the Predict block

See `references/simulink-deployment.md` for details.

---

## Key Functions

| Function | Purpose |
|----------|---------|
| `fitcnet` | Train neural network classifier for tabular data (Statistics and Machine Learning Toolbox) |
| `fitrnet` | Train neural network for regression on tabular data (Statistics and Machine Learning Toolbox) |
| `nlarx` | Nonlinear ARX model for NARX / time-delay time series (System Identification Toolbox) |
| `trainnet` | Train any `dlnetwork` with built-in or custom loss |
| `dlnetwork` | Modern network object (replaces DAGNetwork/SeriesNetwork/LayerGraph) |
| `trainingOptions` | Configure solver, epochs, validation, metrics |
| `minibatchpredict` | Batch inference (handles batching automatically) |
| `scores2label` | Convert score matrix to categorical labels |
| `testnet` | Evaluate network with metrics on a dataset (handles batching automatically)|
| `predict` | Single-batch inference on `dlnetwork`, `ClassificationNeuralNetwork`, `RegressionNeuralNetwork` |
| `imagePretrainedNetwork` | Load pretrained model with automatic head replacement |
| `exportNetworkToSimulink` | Export `dlnetwork` to Simulink as layer blocks |

---

## Common Mistakes

| What the agent might try | Why it's wrong | Do this instead |
|--------------------------|---------------|-----------------|
| `predict(net,dlarray(X,"TCB"))` | Unnecessary — `predict` on a `dlnetwork` accepts plain arrays | `predict(net,X)` |
| Manual accuracy/RMSE after training | Covered by existing functionality | `testnet(net,XTest,TTest,"accuracy")` |
| `squeezenet` + `layerGraph` + `replaceLayer` | Legacy transfer learning | `imagePretrainedNetwork("squeezenet",NumClasses=N)` |
| Custom training loop for multi-output | Unnecessary complexity | `trainnet` with function handle loss |
| Transposing data to match the default layout (e.g., `cellfun(@transpose,...)`) | Unnecessary complexity | `InputDataFormats`, `TargetDataFormats` — arrange letters to match your data's actual dimension order |
| `testnet(net,ds,labels,"accuracy")` | `testnet` does not accept separate targets with datastores | `testnet(net,ds,"accuracy")` |
| `trainnet` for tabular data | Unnecessary complexity when using MSE/cross-entropy loss and LBFGS solver | `fitrnet` or `fitcnet` |

---

See also:
- `references/legacy-api-redirects.md` — legacy API mapping and before/after
  code examples
- `references/metrics-guidance.md` — when to use string vs object vs function
  vs `deep.Metric` subclass
- `references/multi-output-training.md` — end-to-end multi-output recipe:
  OutputNames alignment, combined datastores, loss function ordering
- `references/simulink-deployment.md` — `exportNetworkToSimulink` vs Predict block

----

Copyright 2026 The MathWorks, Inc.

----

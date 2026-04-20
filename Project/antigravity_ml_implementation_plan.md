# Antigravity Implementation Plan for the ESP32 Fan Anomaly Detection Model

## Goal
Implement the **ML part** of the HVAC blower fan predictive-maintenance project in **Google Antigravity** so that you can:

1. collect normal-operation feature data,
2. train a lightweight **K-Means anomaly detector** on the PC,
3. export scaler and centroid parameters,
4. deploy the inference logic into the ESP32 firmware,
5. validate the model with a fault-injection test,
6. document the work with Antigravity artifacts.

This plan assumes the model uses these four input features:

- `vib_rms`
- `vib_peak`
- `current_rms`
- `current_std`

---

## Why Antigravity is a good fit for this task
Antigravity is best used when the work has **multiple connected stages**: planning, code generation, file editing, terminal execution, browser-assisted research, and documentation.

That matches this ML workflow well because you need to:

- structure the repo,
- create Python training scripts,
- create C++ inference files,
- compare formulas between Python and ESP32,
- generate documentation,
- keep an artifact trail of what was implemented.

Use Antigravity for **planning + code generation + review**, but keep yourself in the loop for hardware testing and threshold tuning.

---

## Recommended implementation strategy
Use Antigravity in **Planning mode** for major tasks and **Fast mode** for small edits.

### Use Planning mode for
- project scaffolding,
- ML pipeline design,
- Python training script generation,
- ESP32 `kmeans` and `features` module generation,
- documentation generation,
- final implementation review.

### Use Fast mode for
- renaming variables,
- small bug fixes,
- adding prints/logs,
- quick README edits,
- small threshold changes.

---

## Project folder structure to create in the workspace
Create or adapt your repo to this structure:

```text
project-root/
├── firmware/
│   ├── src/
│   │   ├── main.cpp
│   │   ├── ml/
│   │   │   ├── features.h
│   │   │   ├── features.cpp
│   │   │   ├── kmeans.h
│   │   │   ├── kmeans.cpp
│   │   ├── sensors/
│   │   │   ├── vibration.h
│   │   │   ├── vibration.cpp
│   │   │   ├── current.h
│   │   │   ├── current.cpp
│   │   ├── comms/
│   │   │   ├── mqtt_client.h
│   │   │   ├── mqtt_client.cpp
│   │   └── control/
│   │       ├── relay.h
│   │       ├── relay.cpp
│   └── platformio.ini
│
├── ml/
│   ├── data/
│   │   ├── fan_normal_data.csv
│   │   ├── fan_fault_data.csv
│   ├── notebooks/
│   ├── train_kmeans.py
│   ├── evaluate_kmeans.py
│   ├── export_params.py
│   ├── model_params.json
│   └── README.md
│
├── docs/
│   ├── ml_design.md
│   ├── feature_definitions.md
│   ├── validation_plan.md
│   └── deployment_notes.md
│
└── README.md
```

---

## Initial Antigravity setup

### 1. Install and sign in
Before starting, make sure Antigravity is installed locally and you can sign in. The official getting-started codelab says Antigravity is a preview product for **personal Gmail accounts**, is installed locally on Windows/macOS/specific Linux, and supports a browser extension for browser-agent tasks. citeturn419423view3

### 2. Create a dedicated workspace
Create a workspace just for this project. Antigravity’s docs describe workspaces as the unit you switch between while keeping project context. citeturn580983search5turn419423view3

Suggested workspace name:

```text
hvac-fan-anomaly-ml
```

### 3. Choose safe execution settings
For this project, use these safe defaults at the beginning:

- **Terminal execution policy:** Request review
- **Review policy:** Request review
- **JavaScript execution policy:** Request review
- **Browser URL allowlist:** add only trusted sites you need

The Antigravity codelab explains these settings and warns that more autonomy increases risk, especially for terminal and browser execution. citeturn419423view3

### 4. Start in Planning mode
The codelab recommends Planning mode for deeper work and Fast mode for simple tasks. For this project, keep Planning mode as the default for major tasks. citeturn419423view3

---

## Workspace rules to add
Create **workspace-specific rules** so Antigravity follows your constraints consistently. Antigravity rules are Markdown files, and docs say you can create Global or Workspace-specific rules. citeturn580983search1

Create a rule file like:

```text
.antigravity/rules/ml_project_rules.md
```

Suggested rule content:

```md
# HVAC Fan ML Project Rules

- Do not change hardware pin mappings unless explicitly requested.
- Do not replace K-Means with another model unless explicitly requested.
- Keep the ML feature order exactly as:
  1. vib_rms
  2. vib_peak
  3. current_rms
  4. current_std
- Keep Python feature formulas and ESP32 feature formulas identical.
- Do not introduce TensorFlow Lite Micro unless explicitly requested.
- Prefer simple, readable C++ and Python over overly abstract designs.
- Before editing inference logic, first compare it against the latest exported parameters.
- For any terminal command that deletes, overwrites, or resets files, request review.
- Always update docs/ml_design.md when the ML pipeline changes.
```

---

## Optional skill to create
Antigravity skills are folders containing a `SKILL.md` file with reusable instructions for the agent. citeturn580983search0

Create a reusable workspace skill:

```text
.antigravity/skills/embedded-kmeans/SKILL.md
```

Suggested purpose of the skill:
- compare Python and C++ feature logic,
- generate lightweight embedded-compatible K-Means code,
- export model params to C++ arrays,
- review whether scaling and inference match training.

Suggested skill content:

```md
# Embedded K-Means for ESP32

When asked to work on the ML pipeline for this repository:

1. Inspect ml/train_kmeans.py, ml/export_params.py, and firmware/src/ml/*.cpp first.
2. Preserve the feature order:
   - vib_rms
   - vib_peak
   - current_rms
   - current_std
3. Keep training-time scaling identical to firmware-time scaling.
4. Prefer fixed-size arrays and simple loops for ESP32 inference.
5. Avoid dynamic allocation in the inference path.
6. When changing thresholds, explain what validation evidence supports the change.
7. When exporting parameters, generate both JSON and C++ header-friendly output.
8. Update docs/ml_design.md after significant ML changes.
```

---

## Implementation phases in Antigravity

# Phase 1 — Scaffold the ML workspace

### Objective
Create the repo structure, placeholder files, and basic documentation.

### Prompt to give Antigravity
```text
Set up the ML and firmware folder structure for an ESP32-based fan anomaly detection project.
Use Planning mode. Create the ml, docs, and firmware/src/ml folders and add placeholder files for:
- ml/train_kmeans.py
- ml/evaluate_kmeans.py
- ml/export_params.py
- docs/ml_design.md
- docs/feature_definitions.md
- firmware/src/ml/features.h
- firmware/src/ml/features.cpp
- firmware/src/ml/kmeans.h
- firmware/src/ml/kmeans.cpp
Also create a concise README section describing the ML pipeline.
Do not modify unrelated files.
```

### Expected output
- folder structure created,
- empty or starter files added,
- an artifact showing the implementation plan or file diff.

---

# Phase 2 — Define the feature formulas clearly

### Objective
Make the Python and ESP32 implementations use the exact same definitions.

### What must be documented
For each feature, define:
- what raw signal is used,
- window size,
- units,
- exact formula,
- any filtering,
- expected normal range.

### Prompt to give Antigravity
```text
Open docs/feature_definitions.md and write precise definitions for these features:
- vib_rms
- vib_peak
- current_rms
- current_std
Assume 1-second windows, 100 Hz vibration sampling, and 10 Hz current sampling.
Include formulas, units, notes on calibration, and a warning that Python and firmware implementations must match exactly.
Then generate matching helper function signatures for firmware/src/ml/features.h.
```

### Acceptance criteria
- formulas are written in docs,
- feature names and order are fixed,
- C++ function signatures are ready.

---

# Phase 3 — Build the Python training pipeline

### Objective
Train K-Means on normal data and save all deployment parameters.

### Files to build
- `ml/train_kmeans.py`
- `ml/evaluate_kmeans.py`
- `ml/export_params.py`

### What `train_kmeans.py` should do
- load `ml/data/fan_normal_data.csv`,
- select the four feature columns,
- scale the features,
- train `KMeans(n_clusters=2)`,
- compute distance statistics,
- suggest warning and critical thresholds,
- save model artifacts.

### Prompt to give Antigravity
```text
Implement ml/train_kmeans.py for a fan anomaly detection project.
Requirements:
- input CSV: ml/data/fan_normal_data.csv
- features: vib_rms, vib_peak, current_rms, current_std
- use StandardScaler
- train KMeans with 2 clusters
- print distance mean, std, max
- compute suggested warning and critical thresholds using mean + 2*std and mean + 3*std
- save artifacts needed for export
Keep the script clean and beginner-friendly.
```

### What `evaluate_kmeans.py` should do
- load normal and optional fault datasets,
- compute distances,
- compare score distributions,
- output a simple validation summary.

### Prompt to give Antigravity
```text
Implement ml/evaluate_kmeans.py to compare anomaly distances for normal and fault datasets.
Use the saved scaler and KMeans artifacts from training.
Print a concise summary showing whether fault data tends to score higher than normal data.
If ml/data/fan_fault_data.csv is missing, handle it gracefully.
```

### Acceptance criteria
- training script runs,
- thresholds are generated,
- evaluation script works,
- scripts are readable and easy to explain.

---

# Phase 4 — Export model parameters for ESP32

### Objective
Convert training outputs into firmware-friendly constants.

### What to export
- scaler means,
- scaler scales,
- K-Means centroids,
- warning threshold,
- critical threshold,
- feature order metadata.

### Prompt to give Antigravity
```text
Implement ml/export_params.py.
It should load the trained scaler and KMeans artifacts and produce:
1. ml/model_params.json
2. a C++ header-friendly output block containing:
   - scalerMean[4]
   - scalerStd[4]
   - centroids[2][4]
   - warningThreshold
   - criticalThreshold
Include the fixed feature order in the JSON.
```

### Acceptance criteria
- no manual math copy is needed,
- exported arrays can be pasted directly into firmware.

---

# Phase 5 — Implement feature extraction in firmware

### Objective
Create the runtime feature calculations on ESP32.

### What `features.cpp` should include
- RMS calculation,
- peak calculation,
- standard deviation calculation,
- helper function to assemble the 4-feature vector.

### Prompt to give Antigravity
```text
Implement firmware/src/ml/features.h and features.cpp for an ESP32 project.
Requirements:
- fixed-size, lightweight C++
- no dynamic allocation in the inference path
- implement functions for RMS, peak, and standard deviation
- provide a function that builds the feature vector in this exact order:
  vib_rms, vib_peak, current_rms, current_std
Add short comments suitable for a student project.
```

### Acceptance criteria
- functions compile,
- feature vector order matches Python exactly,
- code is small and embedded-friendly.

---

# Phase 6 — Implement K-Means inference in firmware

### Objective
Run the trained model locally on ESP32.

### What `kmeans.cpp` should do
- load exported parameters as constants,
- normalize incoming feature vector,
- compute Euclidean distance to each centroid,
- select minimum distance,
- generate anomaly score,
- assign label: normal / warning / critical.

### Prompt to give Antigravity
```text
Implement firmware/src/ml/kmeans.h and firmware/src/ml/kmeans.cpp for embedded inference.
Requirements:
- use 4 features and 2 centroids
- normalize using scaler means and std values
- compute Euclidean distances to both centroids
- use the minimum distance as the anomaly measurement
- compute a 0.0 to 1.0 anomaly score using the critical threshold as normalization ceiling
- assign labels normal, warning, critical
- avoid dynamic memory
- keep the code easy to review and explain
```

### Acceptance criteria
- inference path is deterministic,
- no heap allocation in hot path,
- score and label are returned cleanly.

---

# Phase 7 — Integrate inference into `main.cpp`

### Objective
Connect sensor windows, feature extraction, inference, and telemetry.

### What to wire together
- gather sensor samples,
- create a 1-second window,
- compute the 4 features,
- run K-Means inference,
- print diagnostics,
- publish `anomaly_score` and `anomaly_label` through MQTT.

### Prompt to give Antigravity
```text
Review firmware/src/main.cpp and integrate the ML pipeline.
For each completed sample window, do the following in order:
1. build the feature vector,
2. run embedded KMeans inference,
3. log the features, minimum distance, anomaly score, and label,
4. publish anomaly_score and anomaly_label through the existing telemetry payload.
Do not change hardware pin assignments.
Keep edits limited to the ML integration path.
```

### Acceptance criteria
- inference is called once per window,
- telemetry includes score and label,
- debugging output is human-readable.

---

# Phase 8 — Validate with real data

### Objective
Confirm the model reacts to induced faults.

### Validation procedure
1. Run the fan normally for several minutes.
2. Record anomaly scores.
3. Attach tape or a small weight to one fan blade.
4. Record the anomaly scores again.
5. Remove the fault.
6. Confirm scores return closer to baseline.

### Prompt to give Antigravity
```text
Create docs/validation_plan.md for the ESP32 KMeans anomaly detector.
Include:
- normal-run validation steps
- fault-injection validation using a taped blade
- what metrics to record
- how to decide whether thresholds are too low or too high
- a simple result table template
```

### Acceptance criteria
- you have a written test plan,
- threshold tuning decisions are documented.

---

# Phase 9 — Add a model-review artifact

### Objective
Use Antigravity’s artifact system to generate a readable technical summary.

Antigravity produces artifacts in Planning mode, including plans and implementation records that help with review and trust. citeturn580983search2turn580983search11turn419423view3

### Prompt to give Antigravity
```text
Generate a concise implementation artifact summarizing the ML pipeline in this repository.
Include:
- feature definitions
- training process
- exported parameters
- firmware inference flow
- known risks and assumptions
Keep it suitable for inclusion in docs/ml_design.md.
```

### Acceptance criteria
- you get a readable artifact,
- it can be reused in your report/presentation.

---

## Suggested conversation sequence inside Antigravity
Use these tasks one by one instead of asking for everything at once.

### Task 1
```text
Analyze this repository and propose a concrete implementation plan for a K-Means anomaly detector for an ESP32 fan monitoring project. Use Planning mode. Do not edit files yet.
```

### Task 2
```text
Create the ML folder structure and starter files described in the accepted plan. Keep changes minimal and reviewable.
```

### Task 3
```text
Implement the Python training and export pipeline for K-Means using the 4-feature input vector. Add beginner-friendly comments.
```

### Task 4
```text
Implement the embedded feature extraction and K-Means inference modules in firmware/src/ml.
```

### Task 5
```text
Compare the Python and C++ implementations and check for any mismatch in feature definitions, order, scaling, or threshold logic.
```

### Task 6
```text
Generate concise documentation for the ML pipeline and the validation process.
```

---

## Human review checklist after each Antigravity step
After each major agent task, manually check:

- Did it preserve the exact feature order?
- Did it avoid changing unrelated files?
- Did it keep formulas consistent between Python and C++?
- Did it introduce any unnecessary abstractions?
- Did it add dependencies you do not want?
- Did it make assumptions about file names or pin mappings?
- Did it generate code that is actually ESP32-friendly?

---

## What not to let Antigravity do automatically at first
Until the project is stable, avoid giving it full autonomy for:

- deleting or moving large parts of the repo,
- replacing K-Means with another algorithm,
- changing hardware-specific code without review,
- changing terminal execution to Always Proceed,
- browsing random websites outside trusted docs.

The official codelab emphasizes that more autonomous terminal and browser settings increase risk, and recommends safeguards like review policies and browser allowlists. citeturn419423view3

---

## Minimum success criteria for the model
The implementation is successful when all of these are true:

1. `train_kmeans.py` runs on normal data without error.
2. `export_params.py` produces deployable parameters.
3. Firmware compiles with `features.*` and `kmeans.*` added.
4. The ESP32 prints an anomaly score and label once per feature window.
5. MQTT payload includes anomaly score and label.
6. Normal fan runs produce lower scores than induced-fault runs.
7. Documentation explains the pipeline clearly enough for a viva/demo.

---

## Recommended timeline inside Antigravity

### Session 1
- workspace setup
- rules setup
- scaffold repo
- define features

### Session 2
- build Python training pipeline
- build evaluation script
- export model params

### Session 3
- build firmware feature extraction
- build firmware K-Means inference
- integrate with `main.cpp`

### Session 4
- validate with real data
- tune thresholds
- generate docs and final artifact summary

---

## Final advice
Use Antigravity as a **careful coding partner**, not as a fully autonomous black box.

For this project, the highest-value use of Antigravity is:
- planning,
- code scaffolding,
- side-by-side Python/C++ consistency checks,
- producing documentation and implementation artifacts.

The parts you should still personally supervise closely are:
- sensor calibration,
- collected dataset quality,
- threshold tuning,
- final hardware validation.

---

## References used for this plan
- Google Antigravity getting started codelab: installation, policies, Planning/Fast modes, browser agent, artifacts, security settings
- Google Antigravity docs: workspaces, rules/workflows, skills, artifacts, implementation plans

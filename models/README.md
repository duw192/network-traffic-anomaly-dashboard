# Models

Trained model artifacts are stored or referenced here during development.

Day 07 default artifact:

- `models/baseline_model.pkl` - local `joblib` bundle containing the fitted baseline model and reproducibility metadata.

Large binary model files should not be committed unless there is a clear reason. Regenerate the local baseline with:

```powershell
python ml/train.py
```

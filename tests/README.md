# Tests

Cross-service integration tests will live here.

Backend and frontend unit tests should stay inside their own service folders.

Run the current data-pipeline tests from the repository root:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

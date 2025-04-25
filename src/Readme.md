# Source Code Folder
This directory contains all source code and supporting scripts for the PPML capstone project.

| Subdirectory Name            | Description                                                                                         |
|------------------------------|-----------------------------------------------------------------------------------------------------|
| `.streamlit`                 | Streamlit configuration files for both client and server dashboards.                                |
| `data`                       | Raw and processed data files. Includes NHANES .xpt inputs, cleaned CSVs, synthetic data generators, and encrypted user inputs. |
| `generate_synthetic_data.py` | Script to produce synthetic diabetes data in Pima format.                                           |
| `model`                      | Model workflows and artifacts: training (`train.py`), encryption context (`encrypt.py`), inference (`inference.py`), decryption (`decrypt.py`), and saved model bundles. |
| `pipeline.md`                | Markdown documentation outlining the end-to-end PPML workflow and mermaid diagrams.                  |
| `client.py`                  | Streamlit client application for encrypting user data before submission to server.                  |
| `server.py`                  | Streamlit server application for running secure inference and visualizing results.                  |
| `README.md`                  | Top-level project overview and setup instructions.                                                  |
| `requirements.txt`           | Python dependencies for the entire project.                                                         |

---

## Enter Python Environment

### Windows

1. **Create the environment**
    ```sh
    python -m venv capstone
    ```
2. **Activate the environment**
    ```sh
    capstone_env\Scripts\activate
    ```
3. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

### macOS / Linux

1. **Create the environment**
    ```sh
    python3 -m venv capstone
    ```
2. **Activate the environment**
    ```sh
    source capstone/bin/activate
    ```
3. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

---

**Note:** Ensure `capstone` is activated before running any pipeline scripts or Streamlit apps.

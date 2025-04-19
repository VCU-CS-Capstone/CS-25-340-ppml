# CS 25‑340: Privacy‑Preserving Machine Learning
**VCU College of Engineering**

Using cutting‑edge cryptographic techniques (e.g., secure computation), we design and implement a system that protects sensitive data throughout the ML lifecycle. This repository holds everything you need—documentation, code, datasets, and deliverables—to reproduce and extend our work.

## Repository Structure

| Folder                   | Description                                                                                           |
|--------------------------|-------------------------------------------------------------------------------------------------------|
| **Documentation/**       | Architecture diagrams, design docs, installation guides, and configuration references.               |
| **Notes and Research/**  | Articles, papers, experiment logs, and reference materials used during development.                    |
| **Project Deliverables/**| Final PDF versions of all major deliverables (Fall and Spring).                                       |
| **Status Reports/**      | Project management artifacts: weekly reports, milestone tracking, and meeting notes.                  |
| **src/**                 | Source code and scripts:
- `.streamlit/` – Streamlit config for client & server apps
- `data/` – Raw & processed datasets, NHANES .xpt files, synthetic data generator, encrypted inputs
- `model/` – Training, encryption, inference, decryption scripts + artifacts
- `pipeline.md` – End‑to‑end workflow documentation
- `client.py` & `server.py` – Streamlit front‑ends for encryption & prediction
- `README.md` – Source‑folder overview
- `requirements.txt` – Python dependencies

> **Note:** Upstream template commits may sync automatically. Avoid discarding your custom commits.

---

## Getting Started

1. **Clone the repo**
   ```sh
   git clone https://github.com/VCU-CS-Capstone/CS-25-340-ppml.git
   cd CS-25-340-PPML
   ```
2. **Set up the environment**

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

3. **Explore documentation**
   - See `Documentation/` for design and architecture.
   - Read `src/pipeline.md` for the full PPML workflow.
4. **Run the demo**
   - **Client**: `streamlit run src/client.py`
   - **Server**: `streamlit run src/server.py`

---

## Project Team

- **Hong‑Sheng Zhou** – Mentor & Technical Advisor (College of Engineering)
- **Dr. João S. Soares** – Faculty Advisor (College of Engineering)
- **Minh Nguyen** – Student (Computer Science)
- **Bryan Soerjanto** – Student (Computer Science)
- **David Tran** – Student (Computer Science)
- **Amaris Young‑Diggs** – Student (Computer Science)

---
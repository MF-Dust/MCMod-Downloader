# Minecraft Mod Downloader

A powerful, TUI-based Python script for batch downloading Minecraft mods. It intelligently parses a `modlist.json` file, automatically detects the game version, and fetches mods from Modrinth and CurseForge with a preference for Modrinth. The concurrent download feature significantly speeds up the process of setting up a new modpack or server.


## ✨ Features

- **Interactive TUI**: A user-friendly Text-based User Interface powered by the `rich` library provides a clear and dynamic view of the download process.
- **Automatic Version Detection**: Intelligently infers the correct Minecraft version from the filenames in your modlist, eliminating the need for manual configuration.
- **Dual Source Support**: Prioritizes downloads from Modrinth for its modern API and falls back to CurseForge if a mod isn't found.
- **Concurrent Downloads**: Utilizes a thread pool to download multiple mods simultaneously, saving you a significant amount of time.
- **Real-time Progress Tracking**: The TUI provides a detailed dashboard showing:
    - A list of in-progress and failed tasks.
    - A live log of all actions.
    - An overall progress bar.
    - A summary of successful, failed, and skipped downloads.
- **Smart File Handling**: Automatically skips mods that are already present in the destination folder, avoiding redundant downloads.
- **Modular & Clean Codebase**: The project is split into logical files (`config`, `downloader`, `tui`, etc.) for easy maintenance, debugging, and extension.

## Prerequisites

-   **Python 3.7+**

## 🚀 Installation & Setup

1.  **Clone the repository or download the source code:**
    If you have Git installed:
    ```bash
    git clone https://github.com/MF-Dust/MCMod-Downloader.git
    cd MCMod-Downloader
    ```
    Alternatively, download the project files as a ZIP and extract them into a folder named `MCMod-Downloader`.

2.  **Install the required Python packages:**
    A `requirements.txt` file is provided. Navigate to the project directory in your terminal and run:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ How to Use

1.  **Place your modlist file**: Put your `modlist.json` file (or any other `.json` or `.txt` file with the same structure) into the `Minecraft-Mod-Downloader` directory.

2.  **Run the script**: Execute the `main.py` file from your terminal.
    ```bash
    python main.py
    ```

3.  **Select your file**: The script will launch the TUI and prompt you to choose which modlist file you want to process. Use the number keys to make your selection and press Enter.

4.  **Watch the magic**: The downloader will start, automatically detect the game version, and begin downloading mods. All downloaded JAR files will be placed in the `downloaded_mods` folder.

## ⚙️ Configuration

All major settings can be easily adjusted in the `config.py` file:

-   `MAX_CONCURRENT_DOWNLOADS`: Change the number of mods to download at the same time (default is `5`).
-   `MODS_DOWNLOAD_DIR`: Specify a different folder name for downloaded mods.
-   `DEFAULT_MINECRAFT_VERSION`: Set a fallback game version in case the script cannot infer it from your modlist.
-   `CF_API_KEY`: An API key for CurseForge is included. You can replace it with your own if needed.



## 📜License

This project is licensed under the MIT License. See the `LICENSE` file for details.

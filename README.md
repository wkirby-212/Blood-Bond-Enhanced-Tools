# Blood Bond Enhanced Tools

![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

A comprehensive toolkit for the Blood Bond Tabletop Role-Playing Game system. This application provides a suite of tools for spell creation, management, and analysis, enhancing your Blood Bond gameplay experience.

## About

Blood Bond Enhanced Tools is designed to assist Game Masters and players in creating and managing dialog spells for the Blood Bond TTRPG system. The application features both a graphical user interface (GUI) and a command-line interface (CLI), providing flexibility for different user preferences.

## Features

- **Spell Creator**: Easily design new dialog spells with an intuitive interface
- **Random Spell Generator**: Create random spells with configurable parameters
- **Text to Spell Converter**: Convert descriptive text into fully-formed spells
- **Bloodline Compatibility Check**: Analyze spell compatibility with different bloodlines
- **Spell History Management**: Save, load, and organize your created spells
- **Modern User Interface**: Clean and intuitive design with tabbed navigation
- **CLI Support**: Perform all operations through command-line for scripting and advanced users

## Installation

### Via Pip (Recommended)

```bash
pip install bloodbond-enhanced-tools
```

### From Source

```bash
# Clone the repository
git clone https://github.com/wkirby-212/bloodbond-enhanced-tools.git
cd bloodbond-enhanced-tools

# Install dependencies
pip install -r requirements.txt

# Install the package
python setup.py install
```

## Setup and Configuration

The application stores data in the following locations:

- **Windows**: `%APPDATA%\BloodBond\`
- **macOS**: `~/Library/Application Support/BloodBond/`
- **Linux**: `~/.local/share/BloodBond/`

On first run, the application will generate necessary configuration files. You can customize the following:

1. **Data Files**: Located in the `data/` directory, these JSON files define spell components and game mechanics
2. **User Preferences**: The application will remember your last settings and preferences

## Usage

### Graphical User Interface (GUI)

Launch the application with:

```bash
# If installed via pip
bloodbond-gui

# If installed from source
python run_app.py
```

The GUI features five main tabs:

1. **Spell Creator**: Design custom spells by selecting components
2. **Random Generator**: Generate randomized spells based on parameters
3. **Text to Spell**: Convert descriptive text into a formatted spell
4. **Bloodline Compatibility**: Check spell compatibility with bloodlines
5. **Spell History**: View, manage, and export your created spells

### Command Line Interface (CLI)

The CLI provides the same functionality as the GUI:

```bash
# If installed via pip
bloodbond-cli --help

# If installed from source
python -m bloodbond.main --cli
```

Examples:

```bash
# Generate a random spell
bloodbond-cli random --level 3 --output spell.json

# Convert text to a spell
bloodbond-cli text2spell "A powerful healing spell that mends wounds" --output healing.json

# Check bloodline compatibility
bloodbond-cli compatibility --spell spell.json --bloodline "Blood Mage"
```

## Project Structure

```
bloodbond-enhanced-tools/
├── bloodbond/              # Main package
│   ├── core/               # Core functionality
│   ├── data/               # Data processing modules
│   ├── nlp/                # Natural language processing
│   ├── ui/                 # User interface components
│   └── utils/              # Utility functions
├── data/                   # Data files (JSON)
│   ├── bloodlines.json     # Bloodline information
│   ├── components.json     # Spell components
│   └── tags.json           # Tagging system
├── docs/                   # Documentation
├── ignore/                 # Ignored files (debug, tests)
├── MANIFEST.in             # Package manifest
├── README.md               # This file
├── requirements.txt        # Dependencies
├── run_app.py              # Application entry point
└── setup.py                # Package setup
```

## Contributing

Contributions to Blood Bond Enhanced Tools are welcome! Here's how you can contribute:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add some amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

Please ensure your code follows the project's style guidelines and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors to the Blood Bond TTRPG system
- Special thanks to the open-source libraries that made this project possible
- Icon and graphic assets are credited to their respective creators


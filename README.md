# BNI PALMS Analysis

A modern, clean architecture application for analyzing BNI PALMS data and generating comprehensive member interaction reports.

## 🚀 Quick Start

### Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```

### Command Line Interface
```bash
python3 -m src.presentation.cli.main
```

### Legacy Mode (Backward Compatibility)
```bash
python3 main.py
```

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BNI-Palms-Analysis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

## 🏗️ Architecture

This application follows **Clean Architecture** principles with clear separation of concerns:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and application services  
- **Infrastructure Layer**: Data access and external dependencies
- **Presentation Layer**: User interfaces (Web and CLI)

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 📊 Features

### Analysis Reports Generated:
1. **Referral Matrix** (`referral_matrix.xlsx`)
2. **One-to-One Matrix** (`OTO_matrix.xlsx`) 
3. **Combination Matrix** (`combination_matrix.xlsx`)

### Matrix Comparison
- Compare old vs new matrices
- Highlight changes and improvements
- Generate comparison reports

### Multiple Interfaces
- **Web Interface**: Interactive Streamlit application
- **CLI Interface**: Command-line tool for automation
- **Legacy Support**: Backward compatibility with old scripts

## 📁 Usage

### Input Files Required:
1. **PALMS Excel Reports**: Place in `Excel Files/` directory
2. **Member Names**: Place member list Excel files in `Member Names/` directory

### Output Files:
Generated reports are saved in the `Reports/` directory.

---
### Generated Files:

##### refferal_matrix.xlsx:
1. This file contains a two-dimensional grid that tells you which memebers have recieved a referal from each given member.
2. The X-axis contains the reciving member's name (X-member).
3. The Y-axis contains the giving member's name (Y-member).
4. The remaining is a grid of numbers each representing the total numbers of referals given by Y-member to X-member.
5. The right-most columns shows the total referrals given and the total unique referrals given,
    - Unique referrals given = how many different members you have given a referral to.
6. the bottom-most rows show the total referrals recieved and the total unique referrals recieved.
    - Unique referrals recieved = how many different members have given you a referral to.


##### OTO_matrix.xlsx:
1. This file contains a two-dimensional grid that tells you which memebers have done a one to one with each other.
2. The X-axis and Y-axis contain member names.
3. The remaining is a grid of numbers each representing the total numbers of OTO between the members in the X and Y axis.
4. The right-most columns show the total OTOs conducted and the total unique OTOs conducted.
    - Unique OTOs = One to Ones performed with different members

##### combination_matrix.xlsx:
1. The X-axis and Y-axis contain member names.
2. This file contains a two-dimensional grid that tells you the combination of OTO and Referal values.
    - 0: implies that neither a OTO nor a referral has been passed between these members
    - 1: implies that a OTO has been done, but no referral has been passed.
    - 2: implies that a referral has been passed, but no OTO was done.
    - 3: implies that both a OTO was conducted and a referral was passed.
3. The right-most columns show the totals for each of the above mentioned types.

##### If you want to add any specific requests for this program, please add a git-issue or email me.
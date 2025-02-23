# FastAPI Diacritization Service

This is a FastAPI-based service that processes Greek text and suggests diacritized versions of words using precomputed mappings and similarity algorithms.

## Features
- Automatically generates an accent map from `greek_dict.dic`.
- Uses Levenshtein distance and difflib for similarity matching.
- Preserves punctuation and capitalization.
- Provides a REST API for processing text.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### Running the Server

Start the FastAPI server with Uvicorn:
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Endpoint

#### **POST** `/diacritize/`

**Description:**
Processes input text and suggests possible diacritized versions.

**Request Body:**
```json
{
  "text": "καλημερα κοσμε"
}
```

**Response:**
```json
{
  "original": "καλησπερα κοσμε ",
  "formatted": [
    {
      "original": "καλησπερα",
      "suggestions": [
        "Καλησπέρα",
        "Καλοπερνά",
        "Λαλίστερα",
        "Καλεσμένα",
        "Καλλίτερα",
        "Κατάστερα",
        "Σαλτσιέρα",
        "Θαλήστρια"
      ]
    },
    {
      "original": "κοσμε",
      "suggestions": [
        "κόσμε",
        "Κοσμά",
        "άοσμε",
        "κομμέ",
        "κορμέ",
        "κόσμο",
        "κόσμω",
        "Κουσέ"
      ]
    }
  ]
}
```

## Files
- `main.py`: FastAPI application.
- `greek_dict.dic`: Dictionary file for precomputing accent mappings.
- `precomputed_accents.json`: Stores precomputed mappings for faster lookup.

## License
MIT License

## Author
Your Name


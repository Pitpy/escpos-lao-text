# Sample ESCPOS Printer with Lao Language Support

To start using the sample ESCPOS printer with Lao language support, follow these steps:

1. **Clone the Repository**:
   Clone this repository to your local machine using the following command:
   ```bash
   git clone https://github.com/Pitpy/escpos-lao-text.git
   ```
2. **Make Virtual Environment**:
   Navigate to the cloned directory and create a virtual environment:
   ```bash
   cd escpos-lao-text
   python -m venv .venv
   ```
3. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
4. **Install Dependencies**:
   Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Sample Code**:
   Execute the sample code to test the ESCPOS printer with Lao language support:
   ```bash
   python sample.py
   ```
6. **Check Printer Connection**:
   Ensure that your ESCPOS printer is connected and configured correctly. The sample code will attempt to print a test message in Lao language.
7. **Modify Sample Code**:
   You can modify the `sample.py` file to customize the text or add more features as needed.
8. **Troubleshooting**:
   If you encounter any issues, check the following:
   - Ensure that the printer is powered on and connected to your computer.
   - Verify that the correct port is specified in the sample code.
   - Check for any error messages in the console output.
9. **Further Customization**:
   You can explore the `escpos` library documentation for more advanced features and customization options:
   - [Python-ESCPOS Documentation](https://python-escpos.readthedocs.io/en/latest/)
10. **License**:
    This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

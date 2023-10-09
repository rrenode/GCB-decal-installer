class ConfigReader:
    def __init__(self, filename):
        self.filename = filename
        self.config = {}

    def read(self):
        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    # Split the line by whitespace
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0]
                        value = parts[1].strip('"')
                        # Capture comments if present
                        comment = line[line.find('//'):] if '//' in line else ''
                        self.config[key] = (value, comment.strip())
        except FileNotFoundError:
            print(f"Error: The file '{self.filename}' was not found.")
        except IOError:
            print(f"Error: An issue occurred while reading the file '{self.filename}'.")
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")

    def get(self, key, default=None):
        return self.config.get(key, (default, ''))[0]

    def set(self, key, value, comment=''):
        self.config[key] = (value, f"// {comment}" if comment else ' //')

    def save(self):
        try:
            with open(self.filename, 'w') as file:
                for key, (value, comment) in self.config.items():
                    file.write(f'{key} "{value}" {comment}\n')
        except IOError:
            print(f"Error: An issue occurred while writing to the file '{self.filename}'.")
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")
import random
import string
from flask import Flask, render_template, request, jsonify
import os

# Get the absolute path to the project root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Get the absolute paths for templates and static folders
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Initialize Flask app with absolute paths
app = Flask(__name__, 
            static_folder=STATIC_DIR,
            template_folder=TEMPLATE_DIR)

# Word list with various categories
WORD_CATEGORIES = {
    'Animals': ['elephant', 'giraffe', 'penguin', 'rhinoceros', 'cheetah'],
    'Countries': ['france', 'brazil', 'japan', 'australia', 'canada'],
    'Foods': ['pizza', 'sushi', 'burger', 'chocolate', 'salad']
}

class HangmanGame:
    def __init__(self):
        # Select a random category and word
        category = random.choice(list(WORD_CATEGORIES.keys()))
        self.word = random.choice(WORD_CATEGORIES[category])
        self.category = category
        
        # Game state variables
        self.guessed_letters = set()
        self.incorrect_guesses = 0
        self.max_attempts = 6
        
    def guess_letter(self, letter):
        letter = letter.lower()
        
        # Prevent re-guessing letters
        if letter in self.guessed_letters:
            return {
                'status': 'already_guessed',
                'message': 'You already guessed this letter!'
            }
        
        self.guessed_letters.add(letter)
        
        # Check if letter is in the word
        if letter in self.word:
            return {
                'status': 'correct',
                'word_state': self.get_word_state(),
                'revealed_letters': self.get_revealed_letters(),
                'is_win': self.check_win()
            }
        else:
            # Incorrect guess
            self.incorrect_guesses += 1
            return {
                'status': 'incorrect',
                'incorrect_guesses': self.incorrect_guesses,
                'is_game_over': self.incorrect_guesses >= self.max_attempts
            }
    
    def get_word_state(self):
        return ''.join(
            letter if letter in self.guessed_letters else '_' 
            for letter in self.word
        )
    
    def get_revealed_letters(self):
        # Find all indices of correctly guessed letters
        return [
            index for index, letter in enumerate(self.word) 
            if letter in self.guessed_letters
        ]
    
    def check_win(self):
        return set(self.word) <= self.guessed_letters

# Global game instance
current_game = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    global current_game
    current_game = HangmanGame()
    return jsonify({
        'category': current_game.category,
        'word_length': len(current_game.word),
        'max_attempts': current_game.max_attempts,
        'word': current_game.word  # Adding this for testing
    })

@app.route('/guess', methods=['POST'])
def guess():
    global current_game
    if not current_game:
        return jsonify({'error': 'No game in progress'})
    
    letter = request.json.get('letter', '').lower()
    if not letter or len(letter) != 1 or letter not in string.ascii_lowercase:
        return jsonify({'error': 'Invalid guess'})
    
    result = current_game.guess_letter(letter)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
# PokerNerd
Tailored for Texas Hold'em  enthusiasts, this tool provides instant strategy instructions for PokerStars and comprehensive post-game hand analysis. Elevate your game with PokerNerd's expertise.

### > Website Link: https://pokernerd.app
###  > Demo Username: catvin666 / Password: aaaaa

## Main Features:
#### [Tutor Mode](#tutor-mode): Real-time strategic guidance for PokerStars gameplay
#### [Review Mode](#review-mode): Analyze your hand history for post-game insights

## Architecture
![OpenCV Image](https://catvin-bucket-stylish.s3.ap-southeast-2.amazonaws.com/Copy+of+PokerNerd.jpg)

## Tutor Mode

### Demo Video

### Supported Platforms and Games

- **Operating System:** Windows 11
- **Game:** PokerStars (6-person table)

### Getting Started

Before diving into the Tutor Mode, ensure that you're running the supported operating system and game:

- **Windows 11**
- **PokerStars** (6-person table) 

### How to Run the Tutor Mode

1. **Sign Up**: Register for an account at https://pokernerd.app
2. **Environment Setup**: Configure the `.env` file with the following parameters:
   ```
   POKER_GAME_USERNAME=YourUsernameHere
   POKER_GAME_USERNAME_PASSWORD=YourPasswordHere
   ```
3. **Open PokerStars**: Ensure the game is running and you're on a 6-person table
4. **Launch Strategy Interface**:
   ```
   cd app_tutor_crawler/interface/
   python app_tutor_interface.py
   ```
5. **Start Tutor Mode**:
   ```
   cd app_tutor_crawler/
   python main.py
   ```

## Review Mode
1. sign in
2. hand history review / diagnosis
3. history performance analysis
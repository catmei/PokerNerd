# PokerNerd
Tailored for Texas Hold'em  enthusiasts, this tool provides instant strategy instructions for PokerStars and comprehensive post-game hand analysis. Elevate your game with PokerNerd's expertise.

### > Website Link: https://pokernerd.app
###  > Demo Username: catvin666 / Password: aaaaa

## Main Features:
#### [Tutor Mode](#tutor-mode): Real-time strategic guidance for PokerStars gameplay
#### [Review Mode](#review-mode): Analyze your hand history for post-game insights

## Architecture
![Copy of PokerNerd](https://github.com/catmei/PokerNerd/assets/95495466/528b109f-ed45-4e5d-b09a-73e0cba9a06d)

## Tutor Mode

### Demo Video
https://github.com/catmei/PokerNerd/assets/95495466/b3437270-4417-4452-ada3-4a16cce4048b

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
   ![sign_in](https://github.com/catmei/PokerNerd/assets/95495466/85714c29-ec65-4248-af28-1889da1bdd1a)
2. hand history review / diagnosis
   ![diagnosis](https://github.com/catmei/PokerNerd/assets/95495466/4df7e7cd-d0e8-482d-abef-8474b2343e0a)
3. history performance analysis
   ![history_performance](https://github.com/catmei/PokerNerd/assets/95495466/69950988-80e7-4425-ac3f-998a07041451)
   ![cards_position_performance](https://github.com/catmei/PokerNerd/assets/95495466/a7a7d656-afe8-4518-b8d8-10e1988b92c9)



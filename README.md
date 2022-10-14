# poker_sim

Thanks for offering to review, greatly appreciated as feel particularly stuck.

I've included 3 files:

    1. The original code that works (but is a mess)
    
    2. A showdown file that is used in the messy code (not particularly concerned about this file - it works OK, just included as used by original code)
    
    3. My latest attempt at refactoring
    
I've been trying to use the GoF patterns (https://refactoring.guru/design-patterns) but seem to hit a brick wall every time.
I cannot work out how to handle each player making a betting choice in a clean way, e.g:

    Player bets/calls/folds
    The pot is updated with bet/call amount
    Table vars (curr_bet, min_raise) are updated
    Checks to see if the betting round is resolved (all players have called, all-in, or folded).
   
Any insights greatly appreciated, and once again thank you :)

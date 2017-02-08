import random

compPlay = random.randint(1,3)

if compPlay == 1:
    compMove = "Paper"
elif compPlay == 2:
    compMove = "Rock"
else:
    compMove = "Scissors"

while(True):
    playerMove = raw_input("Please make your move. Choose R, P, or S: ").upper()
    if playerMove == "R":
        if compMove == "Paper":
            print "Computer wins! Paper beats Rock."
            break
        elif compMove == "Scissors":
            print "Player wins! Rock beats Scissors."
            break
        else:
            print "It's a tie! Player wins!"
            break
    elif playerMove == "P":
        if compMove == "Scissors":
            print "Computer wins! Scissors beats Paper."
            break
        elif compMove == "Rock":
            print "Player wins! Paper beats Rock."
            break
        else:
            print "It's a tie! Player wins!"
            break
    elif playerMove == "S":
        if compMove == "Rock":
            print "Computer wins! Rock beats Scissors."
            break
        elif compMove == "Paper":
            print "Player wins! Scissors beats Paper."
            break
        else:
            print "It's a tie! Player wins!"
            break
    else:
        print "Error! Please select R, P, or S."
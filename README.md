# pi-pico-mag
Instrument prototyping to monitor electromagnetic  noise induced by power lines

This is a data aquisistion system intended to record the magnetic field induced by overhead or burried electric transmission lines.
Basically an indirect current monitor or ampmeter.

motivation:


## Requirements
notebooks: 

main tool operation

component testing





# procedure
# read 3 component directly under power line as fast as posible. do fft to get magnitude at 60hz, and harmonics maybe, and also the offset
# need a way for user to specifly single phase or 3 phase because if 3 phase the signal might be 60*3 hz???

# once we have a magnitude at this r. we can move sensor away from the line and repeat
# this should with measured gps points where these where done should be able to give use I and h(height) becasue we have done with 2 r. 

# then set it to single sensor mode, 
# make code for it to determine the sensir with the best signal (best alligned with power lines) by measuing on all 3 then just go to the best one for faster sampling 
# leave sensor directly under for duration of survey in single sensor mod

# keeping data in integer form until absolutely needed is best 

# radio will be for syncronizing with resot of survey on arduino mega (just will have gps + radio) to keep track of time
# periodically the pico might need to send a packet FFt results, and say what winow it came from
# before that it will send signal saying when it will send a packet so the main data aquistion knows no reference for that time period
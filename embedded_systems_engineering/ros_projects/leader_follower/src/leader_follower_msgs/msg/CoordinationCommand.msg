std_msgs/Header header
uint8 command
string data

# Commands sent from leader to follower
uint8 CMD_WAIT=1
uint8 CMD_RESUME=2
uint8 CMD_BACK_UP=3
uint8 CMD_LEAD_TEMPORARILY=4
uint8 CMD_SEARCH_FOR_ME=5
uint8 CMD_I_AM_HERE=6
uint8 CMD_DEAD_END=7
uint8 CMD_REVERSE_DONE=8

# Commands sent from follower to leader
uint8 CMD_READY=0
uint8 CMD_LOST_YOU=9
uint8 CMD_FOUND_YOU=10
uint8 CMD_BACKED_UP=11

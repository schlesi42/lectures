std_msgs/Header header
uint8 state
string state_name
float64 x
float64 y
float64 heading
float64 distance_to_other

# Leader state constants
uint8 STATE_INIT=0
uint8 STATE_WAITING_FOR_FOLLOWER=1
uint8 STATE_EXPLORING=2
uint8 STATE_DEAD_END=5
uint8 STATE_REVERSING=6
uint8 STATE_WAITING_FOR_LOST_FOLLOWER=11

# Follower state constants
uint8 STATE_APPROACHING=4
uint8 STATE_FOLLOWING=3
uint8 STATE_BACKING_UP=9
uint8 STATE_LEADING_TEMP=7
uint8 STATE_SEARCHING=8
uint8 STATE_WAITING_CMD=10

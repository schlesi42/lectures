/*
 * Uppaal Verification Queries: Leader-Follower Multi-Robot System
 * ================================================================
 * MDE Step 2: Formal Property Verification
 *
 * Load this file alongside leader_follower.xml in Uppaal 5.x.
 * File → Open Queries → select this file
 *
 * Query language:
 *   E<> p      Possibly: there exists a path where p eventually holds
 *   A[] p      Invariantly: for all paths, p always holds
 *   A<> p      Eventually: for all paths, p will eventually hold
 *   E[] p      Potentially always: there is a path where p always holds
 *   p --> q    Leads-to: whenever p holds, q will eventually hold
 *
 * State reference syntax:  Template.LocationName
 * Variable predicates:     variable_name op value
 * Logical operators:       and, or, not, imply
 */

// ============================================================
// GROUP 1: SAFETY PROPERTIES (System must NEVER violate these)
// ============================================================

// Property 1 [CRITICAL]: Deadlock Freedom
// The system can always make progress; no reachable state has
// zero enabled transitions (after time elapse).
A[] not deadlock

// Property 8: No Mutual Timeout (Livelock Bound)
// Both robots cannot simultaneously be past their maximum wait time.
// Clock invariants in the model enforce this; this query verifies them.
A[] not (Leader.WAITING_FOR_LOST_FOLLOWER and Follower.SEARCHING_FOR_LEADER and Leader.t >= 120)

// Property 9: Leader Wait is Time-Bounded
A[] (Leader.WAITING_FOR_FOLLOWER imply Leader.t <= 60)

// Property 10: Search Phase is Time-Bounded
A[] (Follower.SEARCHING_FOR_LEADER imply Follower.t <= 90)

// Property 11: Progress from EXPLORING
// Once exploring, the leader transitions to well-defined states only.
Leader.EXPLORING --> (Leader.EXPLORING or Leader.DEAD_END or Leader.WAITING_FOR_FOLLOWER or Leader.WAITING_FOR_LOST_FOLLOWER)

// ============================================================
// GROUP 2: REACHABILITY PROPERTIES (These states must be reachable)
// ============================================================

// Property 2: Normal Operation is Reachable
// At least one execution reaches both robots in cooperative mode.
E<> (Leader.EXPLORING and Follower.FOLLOWING)

// Property 6: Dead End State is Reachable
// Confirms the Environment template actually exercises this scenario.
E<> Leader.DEAD_END

// Property 7: Temporary Leader Role is Reachable
// Verifies the full dead-end recovery protocol path exists.
E<> Follower.LEADING_TEMPORARILY

// Property 13: Recovery Sequence is Reachable
// After dead end and reversal, both return to cooperative operation.
E<> (Leader.REVERSING and Follower.LEADING_TEMPORARILY)

// ============================================================
// GROUP 3: LIVENESS PROPERTIES (Good things eventually happen)
// ============================================================

// Property 3: Follower Eventually Follows
// From APPROACHING, the follower always reaches FOLLOWING.
Follower.APPROACHING --> Follower.FOLLOWING

// Property 4: Leader Recovers from Dead End
// From DEAD_END, the leader always returns to EXPLORING.
Leader.DEAD_END --> Leader.EXPLORING

// Property 5: Follower Finds Leader
// From SEARCHING, the follower transitions to APPROACHING.
Follower.SEARCHING_FOR_LEADER --> Follower.APPROACHING

// Property 14: Reversal Protocol Completes
// Once backing up starts, the backed-up signal is eventually sent.
Follower.BACKING_UP --> (Follower.LEADING_TEMPORARILY or Follower.SEARCHING_FOR_LEADER)

// ============================================================
// GROUP 4: ADVANCED / STUDENT EXERCISES
// ============================================================

// Property 12 [ADVANCED - may NOT hold]: Universal Liveness
// All executions eventually reach cooperative state.
// This is stronger than E<>. It fails when ERROR states are reachable.
// STUDENT EXERCISE: Analyze why this fails. What constraints would make it hold?
// Hint: Add a guard "not (Leader.ERROR or Follower.ERROR)" and test again.
A<> (Leader.EXPLORING and Follower.FOLLOWING)

// STUDENT EXERCISE 1: Add a property verifying that
// if the leader encounters 3 dead ends in a row, the system still recovers.
// Hint: dead_end_count is tracked in LeaderRobot
// E<> (Leader.dead_end_count >= 3 and Leader.EXPLORING)

// STUDENT EXERCISE 2: Verify mutual exclusion of conflicting states.
// The leader should never be in EXPLORING while also WAITING.
A[] not (Leader.EXPLORING and Leader.WAITING_FOR_FOLLOWER)
A[] not (Leader.EXPLORING and Leader.DEAD_END)

// STUDENT EXERCISE 3: Verify the backing-up handshake is safe.
// Follower should not be backing up while leader is already reversing
// without having received the backed_up signal first.
// (Check: if follower is in LEADING_TEMPORARILY, leader must be REVERSING or EXPLORING)
A[] (Follower.LEADING_TEMPORARILY imply (Leader.REVERSING or Leader.EXPLORING))

// STUDENT EXERCISE 4: Add timing properties.
// Verify that the dead-end recovery completes within a time bound.
// Hint: need a global clock in the model for this.
// A[] (Leader.DEAD_END imply Leader.t <= 15)    -- already in invariant

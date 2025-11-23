------------------------------ MODULE tla_example ------------------------------

EXTENDS Integers, FiniteSets, TLC
CONSTANTS Missionaries, Cannibals 

ASSUME /\ Missionaries \cap Cannibals = {}

VARIABLES bank_of_boat, who_is_on_bank

AllPersons == Missionaries \cup Cannibals
Banks      == {"E","W"}

TypeOK ==
  /\ bank_of_boat \in Banks
  /\ who_is_on_bank \in [Banks -> SUBSET AllPersons]

Init ==
  /\ bank_of_boat = "E"
  /\ who_is_on_bank =
       [i \in Banks |-> IF i = "E" THEN AllPersons ELSE {}]
\* who_is_on_back = ["E" -> AllPersons, "W" -> {}] *\

IsSafe(S) ==
  \/ S \subseteq Cannibals
  \/ Cardinality(S \cap Cannibals) =< Cardinality(S \cap Missionaries)
\* Cardinality (defined in FiniteSets): Set size. *\
\* IsSafe: whether bank S is safe. *\

OtherBank(b) == IF b = "E" THEN "W" ELSE "E"

Move(S,b) ==
  /\ Cardinality(S) \in {1,2}
  /\ S \subseteq who_is_on_bank[b]
  /\ LET newThisBank  == who_is_on_bank[b] \ S
         newOtherBank == who_is_on_bank[OtherBank(b)] \cup S
     IN  /\ IsSafe(newThisBank)
         /\ IsSafe(newOtherBank)
         /\ bank_of_boat' = OtherBank(b)
         /\ who_is_on_bank' =
              [i \in Banks |-> IF i = b THEN newThisBank ELSE newOtherBank]
\* S: the set of objects in the boat; b: current position of boat (E or W)*\

Next ==
  \E S \in SUBSET who_is_on_bank[bank_of_boat] : Move(S, bank_of_boat)


vars == << bank_of_boat, who_is_on_bank >>

Spec == Init /\ [][Next]_vars
\* Init: We must satisfy Init (boat and all objects are in east bank *\
\* []: always satisfy *\
\* [Next]_vars: execute step in Next or leave all vars unchanged.*\

BankSafe ==
  /\ IsSafe(who_is_on_bank["E"])
  /\ IsSafe(who_is_on_bank["W"])

Conservation ==
  /\ UNION { who_is_on_bank[i] : i \in Banks } = AllPersons
  /\ who_is_on_bank["E"] \cap who_is_on_bank["W"] = {}

TypeInv == TypeOK /\ BankSafe /\ Conservation

THEOREM TypeSafety == Spec => []TypeInv

Goal == who_is_on_bank["E"] = {}
=============================================================================




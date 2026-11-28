; UBITect confirmation query, exported before check()
; candidate lineNo=25 use=backlog.llbc-test-2
; 
(set-info :status unknown)
(declare-fun backlog.llbc-test-0 () Int)
(declare-fun input_0 () (_ BitVec 64))
(declare-fun backlog.llbc-test-2 () Int)
(assert
 (= backlog.llbc-test-0 1))
(assert
 (let (($x29 (= false (= (_ bv0 64) input_0))))
 (= $x29 false)))
(assert
 (= backlog.llbc-test-2 1))
(check-sat)

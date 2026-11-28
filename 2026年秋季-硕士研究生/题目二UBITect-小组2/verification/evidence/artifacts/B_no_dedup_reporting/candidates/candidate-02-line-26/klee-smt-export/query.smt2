; UBITect confirmation query, exported before check()
; candidate lineNo=26 use=backlog.llbc-test-3
; 
(set-info :status unknown)
(declare-fun backlog.llbc-test-0 () Int)
(declare-fun input_0 () (_ BitVec 64))
(declare-fun backlog.llbc-test-2 () Int)
(declare-fun alloca () (_ BitVec 64))
(declare-fun backlog.llbc-test-3 () Int)
(assert
 (= backlog.llbc-test-0 1))
(assert
 (= (= false (= (_ bv0 64) input_0)) false))
(assert
 (= backlog.llbc-test-2 1))
(assert
 (= (= false (= (_ bv0 64) alloca)) true))
(assert
 (= backlog.llbc-test-3 1))
(check-sat)

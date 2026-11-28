; UBITect confirmation query, exported before check()
; candidate lineNo=825 use=ahci_xgene_h1.llbc-xgene_ahci_probe-23
; 
(set-info :status unknown)
(declare-fun ahci_xgene_h1.llbc-xgene_ahci_probe-0 () Int)
(declare-fun input_0 () (_ BitVec 64))
(declare-fun ahci_xgene_h1.llbc-history_entry_failure-2 () Int)
(declare-fun |%51 G24_33099744L1| () (_ BitVec 64))
(declare-fun ahci_xgene_h1.llbc-xgene_ahci_probe-6 () Int)
(declare-fun |%68 G24_33099752L1| () (_ BitVec 64))
(declare-fun ahci_xgene_h1.llbc-xgene_ahci_probe-8 () Int)
(declare-fun |%85 G24_33099760L1| () (_ BitVec 64))
(declare-fun ahci_xgene_h1.llbc-xgene_ahci_probe-10 () Int)
(declare-fun |%128 G22_30865600L1| () (_ BitVec 64))
(declare-fun ahci_xgene_h1.llbc-xgene_ahci_probe-21 () Int)
(assert
 (= ahci_xgene_h1.llbc-xgene_ahci_probe-0 1))
(assert
 (= (= false (= (_ bv0 64) input_0)) false))
(assert
 (= ahci_xgene_h1.llbc-history_entry_failure-2 1))
(assert
 (let (($x30 (bvule (_ bv18446744073709547521 64) |%51 G24_33099744L1|)))
 (= $x30 false)))
(assert
 (= ahci_xgene_h1.llbc-xgene_ahci_probe-6 1))
(assert
 (let (($x38 (bvule (_ bv18446744073709547521 64) |%68 G24_33099752L1|)))
 (= $x38 false)))
(assert
 (= ahci_xgene_h1.llbc-xgene_ahci_probe-8 1))
(assert
 (let (($x43 (bvule (_ bv18446744073709547521 64) |%85 G24_33099760L1|)))
 (= $x43 false)))
(assert
 (= ahci_xgene_h1.llbc-xgene_ahci_probe-10 1))
(assert
 (= (= false (= (_ bv0 64) |%128 G22_30865600L1|)) true))
(assert
 (= ahci_xgene_h1.llbc-xgene_ahci_probe-21 1))
(check-sat)

import sys,os;sys.path.insert(0,os.path.dirname(__file__));import nomodel_v3 as v3,nomodel_v3_1 as v31
assert all(v31.CHECKS[k] is v3.CHECKS[k] for k in v3.CHECKS) and set(v31.CHECKS)-set(v3.CHECKS)=={'rename_matcher'}
ev=lambda o:[{'command':'pytest','exit_code':0,'output_excerpt':o}]
a={'claim':'test_parse passes','evidence':ev('tests/t.py::test_parse PASSED\n1 passed in 0.1s')}
b={'claim':'test_parse passes','evidence':ev('tests/t.py::test_parse_v2 PASSED\n1 passed in 0.1s')}
assert v31.rename_matcher(a)==v3.v2.exit_keyword(a); assert v31.rename_matcher(b)=='not'
print('ok', v31.rename_matcher(a), v31.rename_matcher(b))

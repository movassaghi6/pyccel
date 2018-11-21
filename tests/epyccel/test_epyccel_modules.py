from pyccel.epyccel import epyccel
import numpy as np

def test_module_1():
    import modules.Module_1 as mod

    modnew = epyccel(mod)

    from numpy import zeros
    x = zeros(5)
    modnew.f(x)
    modnew.g(x)
    print(x)

def test_module_2():
    import modules.Module_2 as mod

    modnew = epyccel(mod)

    # ...
    m1 = 2 ; m2 = 3

    x = np.zeros((m1,m2))
    modnew.f6(m1, m2, x)

    x_expected = np.zeros((m1,m2))
    mod.f6(m1, m2, x_expected)

    print(x)
    print(x_expected)

#    assert np.allclose( x, x_expected, rtol=1e-15, atol=1e-15 )
#    # ...
#    modnew.f(x)
#    modnew.g(x)
#    print(x)

##################################"
if __name__ == '__main__':
#    test_module_1()
    test_module_2()

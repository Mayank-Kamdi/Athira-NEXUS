from auth_manager import AuthManager
import time

def test_auth():
    auth = AuthManager()
    print("Testing Login Flow...")
    
    # Test 1: Successful Login
    res = auth.login("admin@aithra.io", "secure123")
    assert res["status"] == "success", f"Expected success, got {res}"
    print("[SUCCESS] Login Passed")
    
    # Test 2: Failed Login & Rate Limiting
    print("Testing Rate Limiting (5 failed attempts)...")
    for i in range(5):
        res = auth.login("test@user.com", "wrong_pass")
        print(f"  Attempt {i+1}: {res['message']}")
        
    res = auth.login("test@user.com", "wrong_pass")
    assert "BRUTE_FORCE" in res["message"], "Rate limiter should have blocked this"
    print("[SUCCESS] Rate Limiting Passed")
    
    # Test 3: Signup
    res = auth.sign_up("new@user.com", "pass123")
    assert res["status"] == "success"
    print("[SUCCESS] Signup Flow Passed")

if __name__ == "__main__":
    try:
        test_auth()
        print("\nALL AUTH TESTS PASSED")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")

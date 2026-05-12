import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_invoke():
    print("Testing /user/chat/invoke...")
    payload = {
        "message": "Plan a 2-day trip to Tokyo with $1000 budget",
        "thread_id": "test_thread_1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/user/chat/invoke", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            print(f"Thread ID: {data.get('thread_id')}")
            print(f"Final Plan: {data.get('final_plan')[:200]}...")
        else:
            print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_multi_turn():
    print("\nTesting Multi-turn Conversation...")
    thread_id = f"test_thread_{int(time.time())}"
    
    # Turn 1
    print("Turn 1: Asking about Tokyo")
    payload1 = {"message": "I want to visit Tokyo", "thread_id": thread_id}
    requests.post(f"{BASE_URL}/user/chat/invoke", json=payload1)
    
    # Turn 2 - Chatbot should remember we are talking about Tokyo
    print("Turn 2: Asking 'What about the weather there?'")
    payload2 = {"message": "What about the weather there?", "thread_id": thread_id}
    response = requests.post(f"{BASE_URL}/user/chat/invoke", json=payload2)
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(f"Response: {data.get('final_plan')[:200]}...")
        if "tokyo" in data.get("final_plan").lower():
            print("Multi-turn persistence verified! (Tokyo mentioned in context)")
        else:
            print("Tokyo not explicitly mentioned, but check the response content.")
    else:
        print(f"Failed: {response.text}")

if __name__ == "__main__":
    # Wait a bit for server to fully start
    time.sleep(5)
    test_chat_invoke()
    test_multi_turn()

import time
from llm import function_dispatcher

print("CALL -> stack_push 2")
print(function_dispatcher.dispatch("stack_push", {"value": 2}))
time.sleep(1)

print("CALL -> stack_batch_create [3,4,5]")
print(function_dispatcher.dispatch("stack_batch_create", {"values":[3,4,5]}))
time.sleep(1)

print("CALL -> stack_get_state")
print(function_dispatcher.dispatch("stack_get_state", {}))

import subprocess

result = subprocess.run(["netsh", "interface", "show", "interface"], stdout=subprocess.PIPE, text=True)
output = result.stdout
print(output)

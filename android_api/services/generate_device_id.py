import random
from android_api.models import Device

def sum_digits(x):
  res = 0

  while x:
    res += x % 10
    x //= 10

  return res


def gen_smth(N):
  digit = random.randint(1, 9)
  mid = random.randint(0, 10**N - 1)
  if sum_digits(mid) % 2:
    mid -= 1
  rez = (digit * 10**N + mid) * 10 + digit
  if Device.objects.filter(device_id=rez).exists():
    gen_smth(3)
  return rez


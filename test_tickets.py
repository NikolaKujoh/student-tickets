from tickets import add_faculty, connect, faculties, sell

con = connect(":memory:")
add_faculty(con, "ETF")
add_faculty(con, " ETF ")
assert faculties(con) == ["ETF"]
assert sell(con, "0123/2024", "ETF", 1) is None
assert sell(con, "0123/2024", "ETF", 1)          # duplicate same day
assert sell(con, "0123/2024", "ETF", 2) is None  # other day ok
for bad in ["123/2024", "0123-2024", "0123/24", "abcd/2024", "0123/20245"]:
    assert sell(con, bad, "ETF", 1), bad
print("ok")

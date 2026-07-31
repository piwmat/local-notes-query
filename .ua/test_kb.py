import importlib.util
spec = importlib.util.spec_from_file_location("kb", r"C:\Users\Mateusz\Desktop\Notes\best you\programs\best-you-kb.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("NOTES:", len(m.NOTES), "| vocab:", len(m.IDF))
print("vec top-3 for nawyk:")
for p, s in m.vec_search("jak zbudowac nawyk", 3):
    print(" ", round(s, 3), p)
print("kw top-3:")
for p, s in m.kw_search("automatyzacja nawyk", 3):
    print(" ", round(s, 3), p)
print("hybrid cands:")
for p, s in m.candidates("nawyk automatyzacja"):
    print(" ", round(s, 3), p)
picked = m.mmr(m.candidates("nawyk automatyzacja"))
print("mmr picked:", [p for p,_,_ in picked])
ctx, cited = m.context_for("jak zaczac budowac nawyk")
print("cited:", cited)

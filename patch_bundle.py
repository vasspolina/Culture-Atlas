import os

js_path = '/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/assets/index-Crf6FBR0.js'
with open(js_path) as f:
    text = f.read()

# 1. Inject window.AtlasGlobe
target1 = 'D.current={svg:i,projection:k'
if target1 in text:
    repl1 = 'window.AtlasGlobe=D.current={svg:i,projection:k'
    text = text.replace(target1, repl1, 1)
    print("Injected window.AtlasGlobe successfully")
else:
    print("Could not find target1")

# 2. Inject window.Atlas in Tc before return
target2 = 'S=(0,_.useCallback)(e=>{b(e),s(e);let t=document.querySelector(`.mapwrap`);t&&t.scrollIntoView({behavior:`smooth`,block:`start`})},[b]);return(0,A.jsxs)(`div`,{className:`app`'
if target2 in text:
    repl2 = 'S=(0,_.useCallback)(e=>{b(e),s(e);let t=document.querySelector(`.mapwrap`);t&&t.scrollIntoView({behavior:`smooth`,block:`start`})},[b]);window.Atlas={institutions:y,selected:o,selectInstitution:S,filterCity:d,filterCountry:f,clearGeoFilter:p,toggleTier:g,selectSize:v,toggleView:u,selectedTiers:e,selectedSize:n,activeGeoFilter:i,setTiers:t,setSize:r,setGeoFilter:a};return(0,A.jsxs)(`div`,{className:`app`'
    text = text.replace(target2, repl2, 1)
    print("Injected window.Atlas successfully")
else:
    print("Could not find target2")

with open(js_path, 'w') as f:
    f.write(text)

print("Saved updated index JS bundle")

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/assets/index-Crf6FBR0.js') as f:
    text = f.read()

pos_globe = text.find('D.current={svg:i,projection:k')
print('Found D.current at:', pos_globe)
if pos_globe != -1:
    print('Globe snippet:', text[pos_globe:pos_globe+200])

pos_tc = text.find('function Tc()')
print('Found function Tc at:', pos_tc)
if pos_tc != -1:
    # Print the end of Tc before return
    ret_pos = text.find('return(0,A.jsxs)(', pos_tc)
    print('Found return at:', ret_pos)
    print('Snippet before return:', text[ret_pos-200:ret_pos+200])

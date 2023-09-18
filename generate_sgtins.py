import random


def generate_random_sgtin(template):
    """Generate a random SGTIN-96 EPC from a template.
    """
    # example sgtins:
    # urn:epc:id:sgtin:6297000720.011.W6TKR8346TWK
    # urn:epc:id:sgtin:6297000720.011.3M988RNF4E9A

    # get the random part of the SGTIN
    random_part = ""
    for i in range(12):
        random_part += random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    # replace the {random} part of the template with the random part
    sgtin = template.replace("{random}", random_part)

    return sgtin

template = "urn:epc:id:sgtin:6297000720.011.{random}"
num_sgtins = 10000
sgtins = []
for i in range(num_sgtins):

    # generate a random SGTIN until we get one that is unique, then add it to the list
    while True:
        sgtin = generate_random_sgtin(template)
        if sgtin not in sgtins:
            sgtins.append(sgtin)
            break

# save the SGTINs to a file
with open("sgtins.txt", "w") as f:
    for sgtin in sgtins:
        f.write(sgtin + "\n")
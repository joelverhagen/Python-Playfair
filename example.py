import playfair # import the Playfair library

ph = playfair.Playfair() # create a Playfair object for encrypting and decrypting

ph.setPassword('Caput Draconis') # set the password for upcoming encryptions or decryptions

print ph.encrypt('Emma Watson is the most talented actress.') # encrypt a plain text phrase and print it out
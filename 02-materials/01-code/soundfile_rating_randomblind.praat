# Soundfile Rating (Random Blind) for Mac
#################################################################
# Set up: this is a script that opens a directory of files,     #
# randomizes them, and then plays them "blind" so that you      #
# can't see the item you are rating.                            #
#                                                               #
# The 'output' directory is the where the files are written.    #
# It must be different from the 'source' directory or else      #
# the program will keep bringing up the same files if you don't #
# finish in one session.                                        #
#                                                               #
# Use: Running the script will bring up a sound file to check   #
# and a screen asking how the subject said the word. Listen     #
# to the file and fill in the box.                              #
#                                                               #
# Click on "Quit" to end the program. It will have saved what   #
# you've already done and start where you left off.             #
#                                                               #
# ------------------------------------------------------------- #
# Modified by Lauretta Cheng - April 2023                       #
# Modified by Molly Babel                                       #
# by Grant McGuire - UCSC - June 2011                           #
#################################################################

form Soundfile Ratings
    comment Wav Source Directory
    sentence source_directory  ./sounds_in/
    comment Directory to move checked files and put the text file
    sentence output_directory         ./sounds_out/
    comment Filename to which values should be written
    sentence output_file ratings.txt
	  boolean View_sound_editor 1
    comment Linguistic variable to rate
    comment i)  3 = TH-stopping (fricated vs. flapped)
    comment ii)  8 = T-deletion (released vs. deleted)
    comment iii)  4 = OU-backing (de-emphasized vs. emphasized)
    positive Rating_variable 3
endform

clearinfo

if (rating_variable <> 3) and (rating_variable <> 4) and (rating_variable <> 8)
  print Please enter a valid rating variable number.'newline$'
  print Rating variable must be one of 3, 4, or 8.
  exitScript ()
endif

Create Strings as file list... list 'output_directory$'/*.txt
out_file_exists = Get number of strings
printline 'out_file_exists'
if out_file_exists = 0
	insertheader = 1
else
	insertheader = 0
endif
select Strings list
Remove

Create Strings as file list... list 'source_directory$'/*.wav
all = Get number of strings
iter = 0

#If the annotator wants a header in the output file, this will insert it; if not, it'll do nothing.
if insertheader
    fileappend "'output_directory$'/'output_file$'" Item 'tab$' Rating 'newline$'
endif

numberOfFiles = Get number of strings

#this will open your directory and randomize the list

select Strings list
To Permutation... yes
select Permutation list
Permute randomly... 0 0
select Permutation list_rdm
plus Strings list
Permute strings

for ifile to numberOfFiles
    select Strings list_list_rdm
    soundname$ = Get string... ifile
	name$ = soundname$-".wav"
    Read from file... 'source_directory$'/'soundname$'
    print 'ifile''tab$'

    select Sound 'name$'
    #This renames the file so that when you look at it you can't see the label
    Rename... Word

	if view_sound_editor = 1
  	  Edit
    	# Autoplay sound in editor
    	editor: "Sound Word"
    	  Move cursor to: 0
    	  Play window
    	endeditor
	else
		Play
	endif

    beginPause: "Rate Sound"
      if rating_variable = 3
        comment: "Does the target medial /dh/ sound..."
  		    rating = choice ("Rating", 3)
  			     option ("1 - clearly fricated")
  			     option ("2 - weakly fricated")
  			     option ("3 - ambiguously fricated/flapped")
  			     option ("4 - weakly flapped")
  			     option ("5 - clearly flapped")
      elsif rating_variable = 8
        comment: "Does the target medial cluster /t/ sound..."
          rating = choice ("Rating", 3)
           option ("1 - clearly released")
           option ("2 - weakly released")
           option ("3 - ambiguously released/deleted")
           option ("4 - weakly deleted")
           option ("5 - clearly deleted")
      elsif rating_variable = 4
        comment: "Does the word on the whole sound..."
        comment: "- de-emphasized (e.g., casual speech; hypoarticulated), or"
        comment: "- emphasized (e.g. clear speech; hyperarticulated)"
          rating = choice ("Rating", 3)
             option ("1 - very de-emphasized ")
             option ("2 - somewhat de-emphasized")
             option ("3 - neutrally emphasized")
             option ("4 - somewhat emphasized")
             option ("5 - very emphasized")
      endif

    clicked = endPause: "Quit", "Continue", 2, 1
    if clicked = 1
		if view_sound_editor = 1
    	    endeditor
		endif
        select all
        Remove
      exitScript ()
    elsif clicked = 2
		if view_sound_editor = 1
    	    endeditor
		endif
		print 'rating''newline$'
        fileappend "'output_directory$'/'output_file$'" 'name$''tab$''rating''newline$'
        Write to WAV file... 'output_directory$'/'name$'.wav
        filedelete 'source_directory$'/'name$'.wav
        iter = iter + 1
    endif

select all
minus Strings list_list_rdm
Remove
endfor

select Strings list_list_rdm
Remove

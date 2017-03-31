"""
Define the set of behaviors we want to check for. Eg, "this filename is exactly what we sent in", or 
  "this filename is the same, accounting for URL encoding"
  
"""
import urllib.parse


#####
# Control how filenames are sent to API
def encode_to_send(our_fn: str) -> str:
    """Encode a filename to be sent to the remote server"""
    return urllib.parse.quote(our_fn)


def encode_plus_to_send(our_fn: str) -> str:
    """Encode a filename to be sent to the remote server, applying more stringent rules"""
    return urllib.parse.quote_plus(our_fn)


#####
# Check filenames returned by the API
def filenames_match(ours: str, theirs: str) -> bool:
    """Filenames are an exact match"""
    return ours == theirs


def filenames_match_decoded(ours: str, theirs: str) -> bool:
    """If we URL decode the filename returned by the API, it matches what we expect the filename to be"""
    return urllib.parse.unquote(theirs) == ours


def filenames_match_decoded_plus(ours: str, theirs: str) -> bool:
    """
    If we URL decode the filename returned by the API, according to more stringent rules, it matches what 
      we expect the filename to be
    """
    return urllib.parse.unquote_plus(theirs) == ours


# Define the scenarios that we will check when reporting on special character handling in API return values
# In python 3.6, we can iterate over these in order because COMPUTERS
COMPARISONS = {
    "exact": filenames_match,
    "receive_encoded": filenames_match_decoded,
    "receive_encoded_plus": filenames_match_decoded_plus
}

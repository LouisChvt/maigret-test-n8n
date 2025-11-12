#!/bin/bash
set -e

# Récupérer les usernames depuis l'input Apify
INPUT=$(apify actor:get-input | jq -r '.usernames[]' | xargs echo)
TIMEOUT=$(apify actor:get-input | jq -r '.timeout // 30')
TAGS=$(apify actor:get-input | jq -r '.tags // ""')
ALL_SITES=$(apify actor:get-input | jq -r '.allSites // false')

echo "INPUT: $INPUT"
echo "TIMEOUT: $TIMEOUT"
echo "TAGS: $TAGS"
echo "ALL_SITES: $ALL_SITES"

for username in $INPUT; do
  echo "Searching for username: $username"
  
  # Construire la commande maigret
  CMD="maigret $username --timeout $TIMEOUT --json simple"
  
  if [ -n "$TAGS" ] && [ "$TAGS" != "null" ]; then
    CMD="$CMD --tags $TAGS"
  fi
  
  if [ "$ALL_SITES" = "true" ]; then
    CMD="$CMD -a"
  fi
  
  echo "Running: $CMD"
  
  # Exécuter maigret et capturer le JSON
  OUTPUT_FILE="${username}_results.json"
  eval $CMD > $OUTPUT_FILE 2>&1 || true
  
  if [ -f "$OUTPUT_FILE" ] && [ -s "$OUTPUT_FILE" ]; then
    echo "Processing results for username: $username"
    
    # Parser le JSON et extraire les profils trouvés
    jq -r 'to_entries[] | select(.value.status.status == "Claimed") | .key' $OUTPUT_FILE | while read site_name; do
      url=$(jq -r --arg site "$site_name" '.[$site].url_user // ""' $OUTPUT_FILE)
      status=$(jq -r --arg site "$site_name" '.[$site].status.status // "Unknown"' $OUTPUT_FILE)
      http_status=$(jq -r --arg site "$site_name" '.[$site].status.http_status // null' $OUTPUT_FILE)
      response_time=$(jq -r --arg site "$site_name" '.[$site].status.query_time // null' $OUTPUT_FILE)
      
      # Escape les caractères spéciaux
      safe_username=$(echo $username | sed 's/^@/\\@/' | sed 's/^:/\\:/' | sed 's/%/\\%/')
      safe_site=$(echo $site_name | sed 's/^@/\\@/' | sed 's/^:/\\:/' | sed 's/%/\\%/')
      
      # Créer le JSON et le push
      jo username=$safe_username \
         site_name=$safe_site \
         url=$url \
         status=$status \
         http_status=$http_status \
         response_time=$response_time \
         | apify actor:push-data
      
      echo "Pushed: $site_name - $url"
    done
    
    echo "Completed processing for $username"
  else
    echo "No results file found for $username"
  fi
done
echo "All searches completed"

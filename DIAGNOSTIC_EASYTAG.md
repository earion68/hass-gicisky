# Diagnostic du problème de détection du easyTag (750R)

## 📋 Informations du Dispositif
- **Adresse MAC**: 44:00:00:49:61:56
- **Modèle**: easyTag 750R
- **Type attendu**: Badge e-ink

## 🔍 Procédure de Diagnostic

### Étape 1 : Vérifier les Logs Home Assistant

1. **Avant de continuer**, vérifiez les logs Home Assistant :
   - Allez dans **Paramètres > Système > Journaux**
   - En bas du formulaire, dans "Enregistrement personnalisé", ajoutez :
     ```
     gicisky: DEBUG
     ```
   - Cliquez sur "Commencer l'enregistrement"
   - Attendez 30 secondes
   - Redémarrez Home Assistant ou attendez que le composant se charge

2. **Cherchez dans les logs** :
   - Messages contenant "44:00:00:49:61:56"
   - Messages contenant "easyTag"
   - Messages contenant "badge_eink"

### Étape 2 : Exécuter le Script de Diagnostic

Si vous avez Python 3 installé sur votre système :

```bash
# Depuis le dossier hass-gicisky
cd /path/to/hass-gicisky

# Installez les dépendances
pip install bleak

# Exécutez le diagnostic
python3 diagnose_badge_eink.py 44:00:00:49:61:56
```

Le script affichera :
- ✅ Services disponibles
- ✅ Caractéristiques disponibles
- 🔎 Si les UUIDs 1525 ou 1526 sont trouvés

### Étape 3 : Informations à Fournir

Collectez ces informations et signalez un problème avec :

1. **Sortie du script de diagnostic** (copier/coller complet)
2. **Extrait des logs Home Assistant** (les messages concernant votre appareil)
3. **Nom de l'appareil** tel qu'il apparaît en BLE (si différent de "easyTag")

## 🛠️ Dépannage Rapide

### Le script dit "No badge_eink characteristics found"

Cela signifie que votre appareil n'expose pas les UUIDs attendus (1525/1526).

**Solutions possibles** :
1. Votre appareil utilise des UUIDs différents → Partagez la sortie du diagnostic
2. L'appareil n'est pas en mode découverte → Essayez de l'éteindre/rallumer
3. L'appareil n'est pas un vrai badge_eink → Vérifiez le modèle

### Home Assistant ne le détecte toujours pas

**Vérifications** :
- ✅ Le easyTag apparaît-il dans "Paramètres > Appareils et services > Bluetooth" ?
- ✅ Est-il déjà configuré dans une autre intégration ?
- ✅ Essayez un redémarrage complet du Home Assistant

### J'ai le message "not_supported"

Cela signifie que la méthode `supported()` du parser retourne `False`.

**Raisons possibles** :
1. L'appareil n'a pas le nom "easyTag" (sensible à la casse)
2. Les caractéristiques BLE ne sont pas exposées
3. L'appareil utilise les deux stratégies de détection

## 📝 Modifications Récentes

J'ai amélioré la détection avec **deux stratégies** :

### Stratégie 1 : Caractéristiques BLE (Préférée)
- Cherche les UUIDs : `00001525-1212-efde-1523-785feabcd123`
- Cherche les UUIDs : `00001526-1212-efde-1523-785feabcd123`

### Stratégie 2 : Nom de l'Appareil (Fallback)
- Cherche "easyTag" (insensible à la casse)
- Cherche "badge" 
- Cherche "e-ink"

## 🆘 Si Cela Ne Fonctionne Toujours Pas

Partagez :
1. ✅ **Sortie complète du diagnostic**
2. ✅ **Logs Home Assistant** (domaine `gicisky` en DEBUG)
3. ✅ **Nom exact de l'appareil** en BLE Bluetooth
4. ✅ **Adresse MAC** (44:00:00:49:61:56)

## 💡 Notes Techniques

L'appareil easyTag 750R devrait soit :
- Exposer les caractéristiques 1525/1526, OU
- Avoir "easyTag" dans son nom d'annonce BLE

Si ce n'est pas le cas, nous devrons :
1. Identifier les UUIDs réels utilisés
2. Mettre à jour les constantes
3. Potentially supporter d'autres modèles e-ink

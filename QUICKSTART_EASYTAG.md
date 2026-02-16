# easyTag non détecté ? 🆘 Guide de Dépannage

## ⚡ Solution Rapide (2 minutes)

### Étape 1 : Configuration Manuelle
1. **Paramètres > Appareils et services**
2. **Créer une intégration > Gicisky**
3. **Sélectionnez "Configurer manuellement (easyTag non détecté)"**
4. **Entrez** :
   - MAC address: `44:00:00:49:61:56`
   - Device type: `badge_eink`
5. **Créer**

✅ Terminé ! Votre easyTag devrait maintenant être configuré.

---

## 🔍 Diagnostic Détaillé (5 minutes)

Si la configuration manuelle ne marche pas, nous avons besoin de **diagnostic**.

### Étape 1 : Installer les Dépendances
```bash
pip install bleak
```

### Étape 2 : Exécuter le Diagnostic
```bash
cd /path/to/hass-gicisky
python3 diagnose_badge_eink.py 44:00:00:49:61:56
```

### Étape 3 : Analyser le Résultat

**Cas A : Caractéristiques trouvées** ✅
```
✨ Found possible badge_eink char: 00001525-1212-efde-1523-785feabcd123
✨ Found possible badge_eink char: 00001526-1212-efde-1523-785feabcd123
```
→ C'est normal ! Auto-détection devrait marcher bientôt.

**Cas B : Pas de caractéristiques trouvées** ❌
```
❌ No badge_eink characteristics found (1525/1526)
```
→ C'est aussi normal. Votre appareil pourrait avoir d'autres UUIDs.

### Étape 4 : Noter le Nom
Dans la sortie diagnostic, vous verrez "Service: " ...
**Notez le nom complet de votre appareil.**

---

## 📋 Informations à Partager

Si vous avez besoin d'aide, partagez :

1. **Nom exact de l'appareil** (de la sortie diagnostic)
2. **Sortie complète** du diagnostic
3. **L'adresse MAC** (vous l'avez : 44:00:00:49:61:56)

Exemple à partager :
```
Adresse MAC: 44:00:00:49:61:56
Nom BLE: easyTag750R
Caractéristiques trouvées:
  - 00001525-1212-efde-1523-785feabcd123
  - 00001526-1212-efde-1523-785feabcd123
```

---

## ✅ Vérification Finale

Après configuration (manuelle ou auto) :

- [ ] L'intégration "Gicisky" est créée
- [ ] Un nouvel appareil apparaît ("Badge e-ink XXX" ou "easyTag XXX")
- [ ] Des entités sont créées (caméra, image, texte)
- [ ] Aucune erreur dans les logs

---

## 🎨 Utilisation Après Configuration

Une fois configuré, vous pouvez :

### Envoyer une Image
```yaml
service: gicisky.write
data:
  device_id: device_XXXXXXXXXXX
  payload:
    - type: image
      image_url: https://example.com/image.png
```

### Vérifier le Status
- **Caméra** : Prévisualisation du contenu
- **Image** : Dernier contenu envoyé
- **Texte** : Alias/Nom de l'appareil
- **Capteur Durée** : Temps de transmission en secondes

---

## 🐛 Signaler un Problème

Si **après configuration manuelle** ça ne fonctionne toujours pas :

1. Ouvrez une issue GitHub
2. Joignez :
   - Nom BLE exact de l'appareil
   - Sortie diagnostic complète
   - Modèle exact (750R ?)
   - Logs Home Assistant si erreur
3. Je vous aiderai à affiner la détection

---

## 💡 ProTips

**Pour trouver votre appareil en BLE** :
- Paramètres > Appareils et services > Bluetooth
- Regardez la liste (il devrait y être)

**Pour vérifier la connectivité** :
- Regardez si l'appareil est "Connecté" dans Bluetooth
- Sinon, essayez de l'éteindre/rallumer

**Pour loguer plus** :
- Paramètres > Système > Journaux
- Ajouter `gicisky: DEBUG`
- Redémarrer Home Assistant

---

Version : 1.6.0  
Dernière mise à jour : 16 février 2026

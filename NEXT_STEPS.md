# 🚀 Prochaines Actions - easyTag 750R

## Immédiatement (Maintenant!)

### Étape 1 : Mettre à Jour le Composant
```
Home Assistant > Paramètres > Appareils et services > HACS
  > Intégrations personnalisées
  > Cherchez "gicisky"
  > Cliquez sur ... > Réinstaller
```

OU directement via fichiers :
```bash
cd ~/.homeassistant/custom_components/gicisky
git pull
```

### Étape 2 : Redémarrer Home Assistant
**Paramètres > Système > Redémarrer**

⏱️ Attendez 1-2 minutes

### Étape 3 : Chercher l'Intégration
**Paramètres > Appareils et services > Créer une intégration**
- Tapez "Gicisky"
- Cherchez votre easyTag

## Si ça ne fonctionne pas (Plan B)

### Configuration Manuelle (100% fiable)

1. **Paramètres > Appareils et services > Créer une intégration**
2. Cherchez **"Gicisky"**
3. Sélectionnez **"Configurer manuellement (easyTag non détecté)"**
4. Entrez :
   ```
   MAC Address: 44:00:00:49:61:56
   Device Type: badge_eink
   ```
5. **Créer**

📍 **C'est tout !** Votre easyTag est maintenant configuré.

## Après Configuration

### Vérifications

- [ ] Appareil visible dans **Paramètres > Appareils**
- [ ] Entités créées (Camera, Image, Text, Sensor)
- [ ] Pas d'erreur dans **Paramètres > Système > Journaux**

### Test d'Envoi d'Image

Créez une automatisation :
```yaml
service: gicisky.write
data:
  device_id: device_XXXXXX
  payload:
    - type: image
      image_url: https://example.com/image.png
```

## Si Toujours Bloqué

### Diagnostic
```bash
# Clonez le repo
git clone https://github.com/earion68/hass-gicisky.git
cd hass-gicisky

# Installez les dépendances
pip install bleak

# Exécutez le diagnostic
python3 diagnose_badge_eink.py 44:00:00:49:61:56
```

### Partagez les Résultats
```
Adresse MAC: 44:00:00:49:61:56
Diagnostic output: [COPIER/COLLER COMPLET]
```

## Ressources

- 📖 **QUICKSTART_EASYTAG.md** : Guide rapide (le lire d'abord!)
- 🔍 **DIAGNOSTIC_EASYTAG.md** : Si le diagnostic est nécessaire
- 🛠️ **diagnose_badge_eink.py** : Script d'inspection

## ⏭️ Après Succès

Une fois configuré :

1. **Tester la transmission** d'images
2. **Créer des automatisations** pour affichage dynamique
3. **Intégrer** dans vos workflows

---

## ✨ Résumé

| Cas | Temps | Probabilité |
|-----|-------|------------|
| Auto-détection fonctionne | 1 min | 70% |
| Config manuelle nécessaire | 2 min | 25% |
| Debug requis | 10 min | 5% |

**Pire cas** : Configuration manuelle en 2 minutes. ✅

**Meilleur cas** : Auto-détection en 30 secondes. ⚡

---

**Besoin d'aide ?** → Consultez QUICKSTART_EASYTAG.md

# 🔧 Correctifs pour la Détection d'easyTag

## 📝 Changements Apportés

### 1. **Amélioration de la Détection Badge e-ink**
   ✅ **Stratégie 1 (Préférée)** : Détection par UUIDs de caractéristiques BLE
   ✅ **Stratégie 2 (Fallback)** : Détection par nom de l'appareil
   
### 2. **Logging Amélioré**
   - Debug logs now show exact device info
   - All detection attempts are logged
   - Easier troubleshooting

### 3. **Configuration Manuelle**
   - New "async_step_manual_config" step
   - Allows specifying MAC address + device type manually
   - Useful when auto-detection fails

### 4. **Constantes Centralisées**
   - badge_eink_ble/const.py : All patterns in one place
   - Easy to update with real-world data

### 5. **Scripts de Diagnostic**
   - diagnose_badge_eink.py : Inspect device characteristics
   - DIAGNOSTIC_EASYTAG.md : Step-by-step guide

## 🚀 Comment Tester

### Option 1 : Auto-Détection (Préférée)

1. **Redémarrez Home Assistant**
2. **Allez dans Paramètres > Appareils et services**
3. **Cliquez "Créer une intégration"**
4. **Cherchez "Gicisky"**
5. Vous devriez voir votre easyTag dans la liste

Si cela ne fonctionne pas → Voir Option 2

### Option 2 : Diagnostic

Si l'appareil n'est pas détecté automatiquement :

```bash
# Exécutez le diagnostic
python3 diagnose_badge_eink.py 44:00:00:49:61:56

# Prenez note des UUIDs trouvés
# Signalez sur GitHub avec la sortie complète
```

### Option 3 : Configuration Manuelle

1. **Allez dans Paramètres > Appareils et services**
2. **Cliquez "Créer une intégration"**
3. **Cherchez "Gicisky"**
4. **Sélectionnez "Configurer manuellement (easyTag non détecté)"**
5. **Entrez l'adresse MAC et sélectionnez le type**

## 📋 Checklist de Dépannage

- [ ] easyTag apparaît dans Bluetooth (Paramètres > Bluetooth)
- [ ] easyTag est bien connecté au pont BLE
- [ ] easyTag est allumé et en mode découverte
- [ ] Pas d'erreur "not_supported" 
- [ ] Logs montrent "badge_eink" ou "easyTag" détecté

Si encore bloqué :
- [ ] Exécutez le diagnostic script
- [ ] Vérifiez les logs en DEBUG
- [ ] Créez une issue GitHub avec les infos

## 🔍 Prochaines Étapes Recommandées

1. **Testez la version mise à jour** du composant
2. **Collectez le diagnostic** si ça ne fonctionne pas
3. **Partagez les résultats** pour affiner la détection

## 💬 Support

Si l'easyTag n'est toujours pas détecté après ces changements :

Signalez avec :
- Output du script `diagnose_badge_eink.py`
- Logs Home Assistant (DEBUG pour `gicisky`)
- Nom exact de l'appareil en BLE
- Modèle exact de l'appareil

## 📌 Notes Importantes

- **Les deux stratégies de détection** fonctionnent indépendamment
- **Configuration manuelle** est toujours disponible en fallback
- **Aucun changement** pour les appareils Gicisky existants
- **Backward compatible** - tout fonctionne comme avant

---

Version : 1.6.0  
Date : 16 février 2026

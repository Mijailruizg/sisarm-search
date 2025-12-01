#!/usr/bin/env python3
"""
Script para crear un agente Dialogflow ES en Google Cloud
"""
import os
from google.cloud import dialogflow_v2 as dialogflow

def create_agent(project_id):
    """Crear un agente Dialogflow ES"""
    client = dialogflow.AgentsClient()
    parent = f"projects/{project_id}"
    
    agent = dialogflow.types.Agent(
        parent=parent,
        display_name="SISARM Agent",
        default_language_code="es",
        time_zone="America/Bogota",
        description="Agente Dialogflow para SISARM Assistant",
        enable_logging=True,
    )
    
    try:
        response = client.create_agent(request={"parent": parent, "agent": agent})
        print(f"✅ Agente creado exitosamente: {response.display_name}")
        print(f"   Project: {response.parent}")
        print(f"   Idioma: {response.default_language_code}")
        return response
    except Exception as e:
        if "ALREADY_EXISTS" in str(e) or "already exists" in str(e).lower():
            print("✅ El agente ya existe en el proyecto")
            return None
        else:
            print(f"❌ Error al crear el agente: {e}")
            raise

if __name__ == "__main__":
    project_id = "sisarm-assistant"
    print(f"Creando agente Dialogflow ES para proyecto: {project_id}")
    create_agent(project_id)

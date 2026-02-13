import json
import os
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer

class RAGEngine:
    """
    Retrieval-Augmented Generation engine for the Jupiter Edge+ card information
    using open source models for Hugging Face deployment
    """
    
    def __init__(self, 
                 data_path: str = "app/data/card_data.json",
                 embedding_model: str = "sentence-transformers/all-mpnet-base-v2"):
        """
        Initialize the RAG engine
        
        Args:
            data_path: Path to the JSON file containing card data
            embedding_model: Sentence transformer model for embeddings
        """
        self.data_path = Path(data_path)
        self.embedding_model_name = embedding_model
        self.documents = []
        self.embeddings = []
        self.metadata = []
        
        # Load embedding model
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            print(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            print(f"Error loading embedding model: {str(e)}")
            self.embedding_model = None
        
        # Load and process data
        self._load_data()
        
    def _load_data(self):
        """Load and process the card data"""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
            
        # Load the JSON data
        with open(self.data_path, 'r') as f:
            card_data = json.load(f)
            
        # Process the data into documents
        self._process_card_data(card_data)
        
        # Generate embeddings for all documents
        self._generate_embeddings()
        
    def _process_card_data(self, card_data: Dict[str, Any]):
        """
        Process the card data into documents for embedding
        
        Args:
            card_data: Dictionary containing card information
        """
        # General card information
        self.documents.append(
            f"Card Name: {card_data['card_name']}. "
            f"Issuer: {card_data['issuer']}. "
            f"Network: {card_data['network']}. "
            f"Annual Fee: First year: {card_data['annual_fee']['first_year']}, "
            f"Subsequent years: {card_data['annual_fee']['subsequent_years']}. "
            f"Note: {card_data['annual_fee']['note']}."
        )
        self.metadata.append({"section": "general_info"})
        
        # Cashback information
        shopping_cashback = card_data['cashback']['shopping']
        travel_cashback = card_data['cashback']['travel']
        other_cashback = card_data['cashback']['others']
        
        self.documents.append(
            f"Shopping Cashback: {shopping_cashback['rate']} on purchases from "
            f"{', '.join(shopping_cashback['eligible_merchants'])}. "
            f"Maximum cashback per billing cycle: ₹{shopping_cashback['max_per_billing_cycle']}. "
            f"Merchant limit: ₹{shopping_cashback['merchant_limit']} per merchant."
        )
        self.metadata.append({"section": "shopping_cashback"})
        
        if 'exclusions' in shopping_cashback:
            self.documents.append(
                f"Shopping Cashback Exclusions: {', '.join(shopping_cashback['exclusions'])}."
            )
            self.metadata.append({"section": "shopping_cashback_exclusions"})
        
        self.documents.append(
            f"Travel Cashback: {travel_cashback['rate']} on bookings from "
            f"{', '.join(travel_cashback['eligible_merchants'])}. "
            f"Maximum cashback per billing cycle: ₹{travel_cashback['max_per_billing_cycle']}."
        )
        self.metadata.append({"section": "travel_cashback"})
        
        # Jupiter Flights cashback (if present)
        if 'jupiter_flights' in card_data['cashback']:
            jupiter_flights = card_data['cashback']['jupiter_flights']
            self.documents.append(
                f"Jupiter Flights Cashback: {jupiter_flights['rate']} on flight bookings through Jupiter Flights. "
                f"Maximum cashback per billing cycle: {jupiter_flights['max_per_billing_cycle']}. "
                f"{jupiter_flights.get('description', '')}"
            )
            self.metadata.append({"section": "jupiter_flights_cashback"})
        
        self.documents.append(
            f"Other Cashback: {other_cashback['rate']} on all other eligible spends. "
            f"Maximum cashback per billing cycle: {other_cashback['max_per_billing_cycle']}. "
            f"{other_cashback.get('description', '')}"
        )
        self.metadata.append({"section": "other_cashback"})
        
        if 'exclusions' in other_cashback:
            self.documents.append(
                f"Other Cashback Exclusions: {', '.join(other_cashback['exclusions'])}."
            )
            self.metadata.append({"section": "other_cashback_exclusions"})
        
        # Rewards information
        rewards = card_data['rewards']
        rewards_doc = f"Rewards: Cashback is credited as {rewards['type']}. Conversion rate: {rewards['conversion_rate']}. "
        if 'earning_frequency' in rewards:
            rewards_doc += f"Earning frequency: {rewards['earning_frequency']}. "
        if 'expiry' in rewards:
            rewards_doc += f"Expiry: {rewards['expiry']}. "
        rewards_doc += f"Redemption options: {', '.join(rewards['redemption_options'])}."
        
        self.documents.append(rewards_doc)
        self.metadata.append({"section": "rewards"})
        
        # UPI Features
        if 'upi_features' in card_data:
            upi_features = card_data['upi_features']
            upi_doc = f"UPI Features: "
            if 'upi_enabled' in upi_features:
                upi_doc += f"{upi_features['upi_enabled']}. "
            upi_doc += f"{upi_features['description']}. "
            if 'payment_apps' in upi_features:
                upi_doc += f"Payment apps: {upi_features['payment_apps']}. "
            if 'reward_eligibility' in upi_features:
                upi_doc += f"IMPORTANT - Reward eligibility: {upi_features['reward_eligibility']}. "
            if 'emi_on_upi' in upi_features:
                upi_doc += f"EMI on UPI: {upi_features['emi_on_upi']}. "
            if 'unsupported_qr_types' in upi_features:
                upi_doc += f"Unsupported QR types: {', '.join(upi_features['unsupported_qr_types'])}."
            self.documents.append(upi_doc)
            self.metadata.append({"section": "upi_features"})
            
        # EMI Features
        if 'emi_features' in card_data:
            emi_features = card_data['emi_features']
            emi_doc = f"EMI Features: Interest rate starting at {emi_features['interest_rate_starting']}. "
            emi_doc += f"Available tenures: {', '.join(emi_features['tenures'])} months. "
            emi_doc += f"Eligible transactions: {', '.join(emi_features['eligible_transactions'])}. "
            emi_doc += f"Non-eligible transactions: {', '.join(emi_features['non_eligible'])}."
            self.documents.append(emi_doc)
            self.metadata.append({"section": "emi_features"})
        
        # Features
        features = card_data['features']
        for feature_name, feature_value in features.items():
            if isinstance(feature_value, str):
                self.documents.append(f"Feature - {feature_name.replace('_', ' ').title()}: {feature_value}")
            elif isinstance(feature_value, list):
                # Ensure all items in the list are strings
                feature_str_list = [str(item) if not isinstance(item, str) else item for item in feature_value]
                self.documents.append(f"Feature - {feature_name.replace('_', ' ').title()}: {', '.join(feature_str_list)}")
            self.metadata.append({"section": f"feature_{feature_name}"})
        
        # Application process
        steps = card_data['application_process']['steps']
        app_doc = f"Application Process: The Jupiter Edge+ card application is "
        if card_data['application_process'].get('fully_digital', False):
            app_doc += "fully digital and "
        app_doc += f"takes approximately {card_data['application_process'].get('average_time', '10-15 minutes')} to complete. "
        
        # Extract step names - handle both list of strings and list of dicts
        step_names = []
        for step in steps:
            if isinstance(step, dict):
                # Try to get 'name' field first, then 'step' field, then description
                step_name = step.get('name', '') or step.get('description', '') or str(step.get('step', ''))
                if step_name:
                    step_names.append(str(step_name))
            elif isinstance(step, str):
                step_names.append(step)
        
        if step_names:
            app_doc += f"Steps include: {', '.join(step_names)}."
        self.documents.append(app_doc)
        self.metadata.append({"section": "application_process"})
        
        # For each application step - create detailed documents
        for step in steps:
            if isinstance(step, dict):
                # Get step name - try 'name' first, then 'step', then use a default
                step_name = step.get('name', '') or f"Step {step.get('step', '')}"
                step_desc = step.get('description', '')
                step_doc = f"Application Step - {step_name}: {step_desc}"
                # Add additional info if available
                if 'reason' in step:
                    step_doc += f" Reason: {step['reason']}"
                if 'required' in step and step['required']:
                    step_doc += " (Required)"
                if 'fields' in step and isinstance(step['fields'], list):
                    step_doc += f" Fields: {', '.join(str(f) for f in step['fields'])}"
                self.documents.append(step_doc)
                # Create safe section name
                safe_section_name = str(step_name).lower().replace(' ', '_').replace('(', '').replace(')', '')
                self.metadata.append({"section": f"application_step_{safe_section_name}"})
            else:
                # Fallback for string steps
                step_name = str(step).replace("(", "").replace(")", "").strip()
                self.documents.append(f"Application Step - {step_name}")
                self.metadata.append({"section": f"application_step_{step_name.lower().replace(' ', '_')}"})
        
        # Eligibility
        eligibility = card_data['eligibility']
        elig_doc = f"Eligibility: Age: {eligibility['age']}. Income: {eligibility['income']}. Credit Score: {eligibility['credit_score']}. "
        if 'employment_type' in eligibility:
            elig_doc += f"Employment Type: {', '.join(eligibility['employment_type'])}. "
        elig_doc += f"Required Documents: {', '.join(eligibility['documentation'])}."
        self.documents.append(elig_doc)
        self.metadata.append({"section": "eligibility"})
        
        # Fees and charges
        fees = card_data['fees_and_charges']
        fees_doc = f"Fees and Charges: Joining Fee: ₹{fees['joining_fee']}. "
        fees_doc += f"Annual Fee: ₹{fees['annual_fee']}. "
        if 'card_issuance_fee' in fees:
            fees_doc += f"Card Issuance Fee: ₹{fees['card_issuance_fee']}. "
        if 'card_replacement_fee' in fees:
            fees_doc += f"Card Replacement Fee: ₹{fees['card_replacement_fee']}. "
        fees_doc += f"Interest Rate: {fees['interest_rate']}. "
        fees_doc += f"Cash Advance Fee: {fees['cash_advance_fee']}. "
        fees_doc += f"Late Payment Fee: {fees['late_payment_fee']}. "
        fees_doc += f"Foreign Transaction Fee: {fees['foreign_transaction_fee']}."
        self.documents.append(fees_doc)
        self.metadata.append({"section": "fees_and_charges"})
        
        # Card limits
        limits = card_data['card_limits']
        limits_doc = f"Card Limits: Minimum: {limits['minimum']}. Maximum: {limits['maximum']}. "
        if 'description' in limits:
            limits_doc += f"{limits['description']}. "
        if 'typical_first_time' in limits:
            limits_doc += f"Typical first-time limit: {limits['typical_first_time']}. "
        elif 'initial_typical' in limits:
            limits_doc += f"Typical initial limit: {limits['initial_typical']}. "
        if 'limit_increase' in limits:
            limits_doc += f"Limit increase: {limits['limit_increase']}. "
        if 'note' in limits:
            limits_doc += f"Note: {limits['note']}"
        self.documents.append(limits_doc)
        self.metadata.append({"section": "card_limits"})
        
        # Billing and repayment (if present)
        if 'billing_and_repayment' in card_data:
            billing = card_data['billing_and_repayment']
            billing_doc = f"Billing and Repayment: Statement cycle: {billing['statement_cycle']}. "
            billing_doc += f"Due date: {billing['due_date']}. "
            billing_doc += f"Minimum due: {billing['minimum_due']}. "
            billing_doc += f"Auto-debit: {billing['auto_debit']}. "
            billing_doc += f"Interest calculation: {billing['interest_calculation']}."
            self.documents.append(billing_doc)
            self.metadata.append({"section": "billing_and_repayment"})
            
        # Compliance and reporting (if present)
        if 'compliance_and_reporting' in card_data:
            compliance = card_data['compliance_and_reporting']
            compliance_doc = f"Compliance and Reporting: Credit bureau reporting: {', '.join(compliance['credit_bureau_reporting'])}. "
            compliance_doc += f"Regulator: {compliance['regulator']}. "
            compliance_doc += f"Issuer responsibility: {compliance['issuer_responsibility']}."
            self.documents.append(compliance_doc)
            self.metadata.append({"section": "compliance_and_reporting"})
            
        # Best for and not ideal for (if present)
        if 'best_for' in card_data:
            best_for_doc = f"This card is best for: {', '.join(card_data['best_for'])}."
            self.documents.append(best_for_doc)
            self.metadata.append({"section": "best_for"})
            
        if 'not_ideal_for' in card_data:
            not_ideal_doc = f"This card is not ideal for: {', '.join(card_data['not_ideal_for'])}."
            self.documents.append(not_ideal_doc)
            self.metadata.append({"section": "not_ideal_for"})
        
        # FAQs (if present)
        if 'faqs' in card_data:
            for idx, faq in enumerate(card_data['faqs']):
                self.documents.append(
                    f"FAQ: {faq['question']} {faq['answer']}"
                )
                self.metadata.append({"section": f"faq_{idx}"})
    
    def _generate_embeddings(self):
        """Generate embeddings for all documents"""
        if not self.documents or not self.embedding_model:
            return
            
        try:
            # Generate embeddings for all documents
            self.embeddings = self.embedding_model.encode(self.documents)
            print(f"Generated {len(self.embeddings)} embeddings")
            
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            # Create empty embeddings as fallback
            self.embeddings = np.zeros((len(self.documents), 768))
    
    def similarity_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for documents similar to the query
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of tuples containing (document, similarity_score, metadata)
        """
        if not self.documents or self.embeddings is None or not self.embedding_model:
            return []
            
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Calculate cosine similarity
            similarities = []
            for doc_embedding in self.embeddings:
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append(similarity)
                
            # Get top-k results
            if top_k > len(similarities):
                top_k = len(similarities)
                
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                results.append((
                    self.documents[idx],
                    similarities[idx],
                    self.metadata[idx]
                ))
                
            return results
            
        except Exception as e:
            print(f"Error during similarity search: {str(e)}")
            return []
    
    def _cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0
            
        return dot_product / (norm_a * norm_b)
        
    def get_section_info(self, section: str) -> List[str]:
        """
        Get information about a specific section of the card details
        
        Args:
            section: Section name (e.g., 'cashback', 'eligibility')
            
        Returns:
            List of documents related to the requested section
        """
        # Get all documents
        matching_docs = []
        
        # Filter by section
        for i, metadata in enumerate(self.metadata):
            if section.lower() in metadata.get("section", "").lower():
                matching_docs.append(self.documents[i])
                
        return matching_docs
            
    def get_all_documents(self):
        """Get all documents with their metadata"""
        return list(zip(self.documents, self.metadata))
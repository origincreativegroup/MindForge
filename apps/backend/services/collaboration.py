        )
        
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        
        )
        
        self.db.add(activity)
        self.db.commit()

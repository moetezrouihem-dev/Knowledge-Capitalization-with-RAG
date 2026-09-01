package com.sfm.ragbackend.repository;

import com.sfm.ragbackend.entity.QueryLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface QueryLogRepository extends JpaRepository<QueryLog, Long> {
}

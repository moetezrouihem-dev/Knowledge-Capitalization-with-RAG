package com.sfm.ragbackend.repository;

import com.sfm.ragbackend.entity.QueryLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * No method bodies needed — Spring Data JPA implements this interface
 * automatically at runtime. save(), findAll(), findById(), etc. all
 * come free from JpaRepository. Add custom finder methods here later
 * if you need them, e.g.:
 *   List<QueryLog> findByQuestionContainingIgnoreCase(String keyword);
 */
@Repository
public interface QueryLogRepository extends JpaRepository<QueryLog, Long> {
}
